# Minute execution scenarios {#provider-a-compatibility}

Language: English · [简体中文](minute-execution.md)

Engine 0.1.0 now provides the minute and leaf evidence APIs described here. See the [current English documentation](https://runchengxie.github.io/quant-backtest-engine/guides/minute-execution/). Platform 0.1.0 preserves existing import paths as aliases of the same Engine objects.

Statistical risk, generic portfolio optimization and integrations awaiting migration remain in Platform; the destination distinguishes their current scope.

[Pre-migration documentation and historical evidence](https://github.com/runchengxie/quant-platform/blob/7a618bddd8fdeee5dbe37fe5b54a9698e0de5355/docs/guides/minute-execution.en.md) retain their original meaning.

Historical v2 checkpoints require their original pinned full release, including the Runtime/Go executable, Python dependency closure and original source bindings. The new provider rejects v2; changing its schema or installing only an old Platform wheel does not provide recovery.

<a id="minute-execution-scenarios"></a>
<a id="conditional-orders-and-declared-information-time"></a>
<a id="temporary-nontrading-mark-provenance"></a>
