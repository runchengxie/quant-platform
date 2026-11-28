# 复用 Qlib 算子的表达式预检

[English](qlib-preflight.en-US.md)

`preflight_qlib_expression` 使用真实 Qlib 算子及其回看、未来窗口元数据。
本地只增加有限语法、字段白名单、角色与版本绑定，没有重写算子计算或新增调度系统。
返回普通 JSON，不返回框架对象，不执行生成的 Python，也不读取行情。

信号默认不允许未来引用。标签可在显式声明的未来期限内使用负向 Ref，
但标签回执不能用作信号准入。admitted 只说明通过了这层表达式检查，
pit_verified 始终为 false，数据发布时间、成分历史、训练窗口和执行价格还需原 owner 审计。

支持 Feature、Ref、Mean、Std、Sum、Min、Max、Rank、Corr、Abs、Log 和基本四则运算。
窗口必须是有限整数，未知算子、属性访问和不安全语法拒绝。
精确限制、六项上下文、调用示例及内容摘要语义见英文正文。

锁定的 Qlib 0.9.7 使用独立 Python 3.12 环境验收，缺少可选依赖时明确 unavailable。
没有把当前服务改为 3.12。原有训练适配器仍直接使用 XGBoost 和本地预处理，
本次不把它宣称为完整 Qlib 后端。
