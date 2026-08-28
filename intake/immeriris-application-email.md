# ImmerIris 数据集申请邮件草稿

> 状态: DRAFT — 2026-08-17 23:0x 由小时简报生成
> 发送阻塞: 本机无 SMTP/himalaya 配置 (无 ~/.config/himalaya), 无法自动发送。
> 请用户: (a) 复制下方任一版本手动发送至 yxmi20@fudan.edu.cn; 或 (b) 配置 himalaya 后由 Agent 代发。
> 联系邮箱: yakeworld@shu.edu.cn | 收件人: yxmi20@fudan.edu.cn (ImmerIris 作者, 复旦大学)

---

## 版本 A — 英文 (CVPR/生物识别社区惯例)

**Subject: Data Access Request — ImmerIris Dataset (CVPR 2026 Oral)**

Dear ImmerIris authors,

I am writing to request access to the ImmerIris dataset introduced in your CVPR 2026
paper (arXiv 2510.10113). I am 杨晓凯 (Xiaokai Yang), MD, PhD candidate-level
principal investigator at the Vertigo Laboratory, Wenzhou Medical University /
Wenzhou People's Hospital, China, and head of its Research & Experiment Center.

My laboratory works on 3D iris morphology and eye-movement modeling. In particular,
we develop Sim2Real pipelines that recover 3D iris shape/pose from 2D images under
unconstrained conditions (our 3diris project cluster). Your dataset's explicit
9 gaze-direction × 11 illumination-level controlled design directly supports two of
our open questions: (1) iris 3D pose recovery from off-axis captures, and (2) the
pupil-iris morphological coupling under controlled illumination (we report a
correlation of r=-0.618 between illumination and pupil/iris morphology on our own data).
The quality-degradation dimensions you annotate (pupil dilation, extreme off-axis,
specular reflection) are, from a morphology perspective, precisely the controlled
variables we need.

We intend to use the data solely for non-commercial academic research. I am happy to
sign any data usage agreement and to cite your work appropriately. If a benchmark
protocol is publicly available, I will start method development with it immediately.

Thank you for considering this request.

Best regards,
Xiaokai Yang (杨晓凯)
Vertigo Laboratory, Wenzhou People's Hospital / Wenzhou Medical University
yakeworld@shu.edu.cn | lab: 3deyes.top

---

## 版本 B — 中文

**主题: ImmerIris 数据集使用申请 (CVPR 2026 Oral)**

尊敬的 ImmerIris 作者团队:

您好!我是温州医科大学/温州市人民医院眩晕实验室的杨晓凯(神经内科主任医师, 科研实验中心主任)。
我们实验室从事虹膜三维形态与眼动建模仿真研究(3diris 项目集群: Sim2Real 虹膜 3D 形状/姿态恢复),
与您的数据集高度契合: 您显式控制的 9 注视方向 × 11 亮度等级, 正是我们两个开放问题的直接数据支撑——
(1) 离轴条件下的虹膜 3D 姿态恢复; (2) 受控光照下瞳孔-虹膜形态耦合(我们自有数据测得 r=-0.618)。
您标注的"质量退化"维度(瞳孔扩张、极端离轴、镜面反射)在我们形态学视角下恰是受控变量。

我们承诺仅用于非商业学术研究, 愿意签署数据使用协议并规范引用。若 benchmark 协议公开,
我们将立即基于公开协议开展方法预研。

期待您的回复, 谢谢!

杨晓凯
温州市人民医院眩晕实验室 / 温州医科大学
yakeworld@shu.edu.cn | 实验室: 3deyes.top

---

## 发送前检查清单
- [ ] 收件人 yxmi20@fudan.edu.cn 是否仍为 ImmerIris 联系邮箱 (来源: 文献监控第37轮报告)
- [ ] 选择英文或中文版本 (或合并)
- [ ] 若配置了 himalaya: `himalaya send -a <account> -t yxmi20@fudan.edu.cn -s "..." < draft.txt`
