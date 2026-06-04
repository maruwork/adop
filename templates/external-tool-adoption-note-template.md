# External Tool Adoption Note Template

**使う場面**: 外部 tool を採るかどうかを整理する時に使う。  
**差し替える所**: tool 名、分類、authority の置き方、trial の状態名。  
**書かないこと**: project 固有の current 運用、正式ルール本文、日々の execution board。

**共通棚として持つもの**: note の骨格だけ。  
**project 側へ出すもの**: current state、実運用 trigger、operator flow、landing target の最終 authority。

## 1. tool

- name:
- source:
- version / date:

## 2. classification

- adoption class: `運用組込` / `作成補助`
- harness layer: `interface` / `mechanism` / `scaling`
- phase: `core build` / `future extension` / `implementation` / `self-improvement loop`

## 3. why this tool

- solved problem:
- why existing repo assets are insufficient:
- why this tool is a better fit than prompt-only operation:

## 4. usage scene

- when to use:
- trigger condition:
- trial executor:
- decision owner:
- who uses it:
- what input it receives:
- what output it produces:

## 5. authority boundary

- authority:
- not authority:
- SSOT writeback target:

## 6. control / verification

- trigger / runbook / hook / queue:
- fail-close:
- escalation:
- verification:
- evaluation gate:
- promote / hold / reject criteria:

## 6.5 trial lifecycle

- trial id:
- current state: `proposed` / `trial-ready` / `in-trial` / `promote` / `hold` / `reject`
- landing target:
- trial start command:
- trial close command:
- artifact:
- observed effect:
- next action:

## 7. repeatability

- one-off or recurring:
- if recurring, what will be promoted:

## 8. current decision

- adopt now / hold / reject:
- follow-up task:
