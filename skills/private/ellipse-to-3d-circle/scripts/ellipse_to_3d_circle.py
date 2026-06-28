"""
ellipse_to_3d_circle — 椭圆逆投影为三维空间圆

输入: 椭圆参数 + 相机内参 + 先验约束
输出: 3D圆心、3D法向量、倾斜角、方位角

Usage:
    python3 ellipse_to_3d_circle.py --ellipse-major 150 --ellipse-minor 120 \
        --ellipse-center 320 240 --rotation 0.3 \
        --focal-length 1500 --camera-cx 320 --camera-cy 240 \
        --prior-radius 10.0 --prior-depth 500.0
"""
import argparse
import numpy as np
import json
import sys
from dataclasses import dataclass, asdict
from typing import Tuple, Optional


@dataclass
class Circle3D:
    center: Tuple[float, float, float]
    radius: float
    normal: Tuple[float, float, float]
    tilt_angle: float
    azimuth_angle: float


@dataclass
class Confidence:
    well_determined: bool
    ambiguity: str  # "none" | "azimuth" | "depth"


@dataclass
class Result:
    circle_3d: Circle3D
    confidence: Confidence


def validate_inputs(a: float, b: float) -> bool:
    """椭圆参数有效性检查"""
    if a <= 0:
        raise ValueError(f"长半轴 a={a} 必须 > 0")
    if not (0 < b <= a):
        raise ValueError(f"短半轴 b={b} 必须在 (0, a={a}] 范围内，b/a = {b/a}")
    return True


def compute_tilt_angle(a: float, b: float) -> float:
    """倾斜角 alpha: cos(alpha) = b/a"""
    validate_inputs(a, b)
    cos_alpha = b / a
    # 防止数值误差
    cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
    return float(np.arccos(cos_alpha))


def compute_normal_from_tilt_and_azimuth(
    tilt: float, azimuth: float
) -> Tuple[float, float, float]:
    """法向量 = (sin(alpha)*cos(phi), sin(alpha)*sin(phi), cos(alpha))"""
    n = (
        np.sin(tilt) * np.cos(azimuth),
        np.sin(tilt) * np.sin(azimuth),
        np.cos(tilt),
    )
    # 单位化
    norm = np.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    return (n[0] / norm, n[1] / norm, n[2] / norm)


def get_azimuth_from_major_axis(
    ellipse_rotation: float,
) -> float:
    """
    从椭圆长轴方向推导方位角。
    
    椭圆长轴方向与相机u轴（水平）夹角为 theta。
    法向量在图像平面上的投影方向与长轴正交。
    
    右手坐标系下：phi = theta + pi/2
    """
    return ellipse_rotation + np.pi / 2.0


def build_orthonormal_basis(normal: Tuple[float, float, float]):
    """构建正交基 (u, v, n)，右手坐标系"""
    n = np.array(normal)
    # 选参考向量
    w = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(n, w)) > 0.9:
        w = np.array([0.0, 1.0, 0.0])  # n 接近 X 轴时换 Y
    
    u = np.cross(w, n)
    u = u / np.linalg.norm(u)
    v = np.cross(n, u)
    v = v / np.linalg.norm(v)
    return u, v, n


def solve_depth_and_center(
    ellipse_center_px: Tuple[float, float],
    focal_length: float,
    camera_cx: float,
    camera_cy: float,
    normal: Tuple[float, float, float],
    circle_radius_mm: float,
    sphere_center_prior: Optional[Tuple[float, float, float]] = None,
) -> Tuple[float, float, float]:
    """
    求解圆心3D坐标。
    
    瞳孔中心 = 椭圆中心投影到3D
    深度由眼球球面约束确定: ||pupil - sphere_center|| = R_eyeball
    """
    # 椭圆中心 → 相机坐标系中的方向
    # u = (u0 - cx) / fx, v = (v0 - cy) / fy
    # 设深度为 z，则 3D点 = (u*z, v*z, z)
    
    u_dir = (ellipse_center_px[0] - camera_cx) / focal_length
    v_dir = (ellipse_center_px[1] - camera_cy) / focal_length
    
    # 瞳孔中心在法向量方向上，距离球心的距离 = R_eyeball
    # 如果提供了球心先验，则：
    # ||(u_dir*z, v_dir*z, z) - C_prior|| = R_eyeball
    
    if sphere_center_prior is not None:
        C = np.array(sphere_center_prior)
        # 求解二次方程: ||d*z - C||^2 = R^2
        d = np.array([u_dir, v_dir, 1.0])
        # (d*z - C)·(d*z - C) = R^2
        # (d·d)*z^2 - 2*(d·C)*z + (C·C - R^2) = 0
        
        A = np.dot(d, d)
        B = -2.0 * np.dot(d, C)
        C_const = np.dot(C, C) - circle_radius_mm ** 2
        
        delta = B ** 2 - 4 * A * C_const
        if delta < 0:
            # 无实数解，退化为沿光轴的深度
            z = C[2] + np.sqrt(circle_radius_mm ** 2 - (C[0] ** 2 + C[1] ** 2))
            if np.isnan(z):
                z = 500.0  # 默认深度
        else:
            z = (-B + np.sqrt(delta)) / (2 * A)  # 取较近的解
        
        center_3d = (u_dir * z, v_dir * z, z)
    else:
        # 无球心先验，深度无法确定 → 返回默认
        center_3d = (u_dir * 500.0, v_dir * 500.0, 500.0)
    
    return center_3d


def ellipse_to_3d_circle(
    major_axis: float,
    minor_axis: float,
    center_px: Tuple[float, float],
    rotation_rad: float,
    focal_length: float,
    camera_cx: float,
    camera_cy: float,
    circle_radius_mm: float,
    prior_depth: float = 500.0,
    sphere_center_prior: Optional[Tuple[float, float, float]] = None,
) -> Result:
    """主函数：椭圆 → 3D圆"""
    
    # Step 1: 基本几何量
    tilt = compute_tilt_angle(major_axis, minor_axis)
    
    # Step 2: 方位角
    azimuth = get_azimuth_from_major_axis(rotation_rad)
    
    # Step 3: 法向量
    normal = compute_normal_from_tilt_and_azimuth(tilt, azimuth)
    
    # Step 4: 深度求解
    center_3d = solve_depth_and_center(
        center_px, focal_length, camera_cx, camera_cy,
        normal, circle_radius_mm, sphere_center_prior
    )
    
    # Step 5: 正交基
    u, v, n = build_orthonormal_basis(normal)
    
    # 确定模糊类型
    ambiguity = "none"
    well_determined = True
    
    if abs(minor_axis - major_axis) < 1e-6:
        # 椭圆退化为圆
        ambiguity = "azimuth"
        well_determined = False
    
    if sphere_center_prior is None:
        ambiguity = "depth"
        well_determined = False
    
    circle_3d = Circle3D(
        center=center_3d,
        radius=circle_radius_mm,
        normal=normal,
        tilt_angle=tilt,
        azimuth_angle=azimuth,
    )
    
    confidence = Confidence(
        well_determined=well_determined,
        ambiguity=ambiguity,
    )
    
    return Result(circle_3d=circle_3d, confidence=confidence)


def main():
    parser = argparse.ArgumentParser(
        description="椭圆逆投影为三维空间圆"
    )
    parser.add_argument("--ellipse-major", type=float, required=True,
                        help="椭圆长半轴 (像素)")
    parser.add_argument("--ellipse-minor", type=float, required=True,
                        help="椭圆短半轴 (像素)")
    parser.add_argument("--ellipse-center", type=float, nargs=2, required=True,
                        help="椭圆中心 (u0, v0) 像素")
    parser.add_argument("--rotation", type=float, default=0.0,
                        help="椭圆长轴旋转角 (弧度)")
    parser.add_argument("--focal-length", type=float, required=True,
                        help="相机焦距 (像素)")
    parser.add_argument("--camera-cx", type=float, required=True,
                        help="光心u")
    parser.add_argument("--camera-cy", type=float, required=True,
                        help="光心v")
    parser.add_argument("--prior-radius", type=float, required=True,
                        help="已知圆半径 (mm)")
    parser.add_argument("--prior-depth", type=float, default=500.0,
                        help="圆心深度先验 (mm)")
    parser.add_argument("--sphere-center", type=float, nargs=3, default=None,
                        help="眼球球心先验 (X, Y, Z) mm")
    
    args = parser.parse_args()
    
    result = ellipse_to_3d_circle(
        major_axis=args.ellipse_major,
        minor_axis=args.ellipse_minor,
        center_px=tuple(args.ellipse_center),
        rotation_rad=args.rotation,
        focal_length=args.focal_length,
        camera_cx=args.camera_cx,
        camera_cy=args.camera_cy,
        circle_radius_mm=args.prior_radius,
        prior_depth=args.prior_depth,
        sphere_center_prior=tuple(args.sphere_center) if args.sphere_center else None,
    )
    
    output = {
        "circle_3d": {
            "center": result.circle_3d.center,
            "radius": result.circle_3d.radius,
            "normal": result.circle_3d.normal,
            "tilt_angle": result.circle_3d.tilt_angle,
            "azimuth_angle": result.circle_3d.azimuth_angle,
        },
        "confidence": asdict(result.confidence),
    }
    
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
