# Recoverable minute execution sessions {#provider-a-compatibility}

Language: English · [简体中文](minute-session.zh-CN.md)

Engine 0.1.0 now provides the minute and leaf evidence APIs described here. See the [current English documentation](https://runchengxie.github.io/quant-backtest-engine/backtest/minute-session/). Platform 0.1.0 preserves existing import paths as aliases of the same Engine objects.

Statistical risk, generic portfolio optimization and integrations awaiting migration remain in Platform; the destination distinguishes their current scope.

[Pre-migration documentation and historical evidence](https://github.com/runchengxie/quant-platform/blob/7a618bddd8fdeee5dbe37fe5b54a9698e0de5355/docs/backtest/minute-session.md) retain their original meaning.

Historical v2 checkpoints require their original pinned full release, including the Runtime/Go executable, Python dependency closure and original source bindings. The new provider rejects v2; changing its schema or installing only an old Platform wheel does not provide recovery.

<a id="recoverable-minute-execution-sessions"></a>
<a id="construct-and-restore"></a>
<a id="financial-clocks-and-ordering"></a>
<a id="external-capital-and-returns"></a>
<a id="delayed-visibility-and-locks"></a>
<a id="checkpoint-version-and-failure-policy"></a>
