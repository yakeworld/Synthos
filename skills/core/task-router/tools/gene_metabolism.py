#!/usr/bin/env python3
"""gene_metabolism.py — behavior 维代谢看门狗 (cycle 269)

每日自检: 报 behavior 分子 (gene_activation 留痕) 增量, 连续 3 天零增量告警"代谢停滞"。
量尺与 diagnose.py v4 的 activation 完全一致:
  outputs/**/pipeline_trace*.json 中含非空 gene_activation 的份数。
no_agent 看门狗: 本脚本 stdout 即交付消息 (每天一行; 停滞时升级 🚨)。
状态: outputs/_runtime/gene_watchdog_state.json
"""
import json, os, glob, time

BASE = os.environ.get('SYNTHOS_DIR', '/media/yakeworld/sda2/Synthos')
STATE = os.path.join(BASE, 'outputs', '_runtime', 'gene_watchdog_state.json')
ZERO_ALERT_DAYS = 3


def scan():
    total = act = 0
    for tf in glob.glob(os.path.join(BASE, 'outputs', '**', 'pipeline_trace*.json'),
                        recursive=True):
        total += 1
        try:
            d = json.load(open(tf))
            if d.get('gene_activation'):
                act += 1
        except Exception:
            pass
    return total, act


def main():
    total, act = scan()
    st = {}
    if os.path.exists(STATE):
        try:
            st = json.load(open(STATE))
        except Exception:
            st = {}
    if st.get('last_activated') is None:
        streak = 0
        msg = (f"🧬 behavior 代谢看门狗基线: 分子 {act}/{total} "
               f"(首跑, 明日开始计增量)")
    else:
        prev_act = st['last_activated']
        delta = act - prev_act
        if delta > 0:
            streak = 0
            msg = f"🧬 behavior 代谢: 分子 {prev_act}→{act} (+{delta}), trace {total} 份, 连停清零"
        else:
            streak = st.get('zero_streak', 0) + 1
            if streak >= ZERO_ALERT_DAYS:
                msg = (f"🚨 代谢停滞告警: 连续 {streak} 天行为增量为 0 "
                       f"(分子 {act}/{total})。检查真实任务是否在走 gene 留痕。")
            else:
                msg = f"🧬 behavior 代谢: 分子 {act} 持平 (0 增量), 连续 {streak} 天无增量"
    st.update({'last_activated': act, 'zero_streak': streak,
               'ts': time.strftime('%Y-%m-%dT%H:%M:%S')})
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(st, open(STATE, 'w'), indent=1)
    print(msg)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
