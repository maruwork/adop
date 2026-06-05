# ADOP

**目的**: 汎用ツール導入管理の共通正本棚。

ここでは、ADOP の共通 code、checklist、template を持つ。
特定 project の current trial 状態や採用 register は持たない。

## これは何か

- `ADOP` は外部 tool 導入判断と trial lifecycle の共通棚
- common authority では artifact schema、trial lifecycle、checklist、template を持つ
- current trial board、operator flow、landing target authority は project-local overlay で持つ

## これは何ではないか

- 特定 project の current adoption board ではない
- 特定 project の operator flow 正本ではない
- 特定 project の landing target authority ではない

## 棚

- `python/`: generic adoption body の共通 code
  - `adop_cli.py`: command entry
  - `adop_artifacts.py`: artifact IO / atomic write
  - `adop_validation.py`: schema / gate validation
  - `adop_summary.py`: summary projection
  - `adop_types.py`: SSOT constants / field names
  - `adop_ids.py`: id mint / parse
  - `adop_state_machine.py`: lifecycle transition helpers
  - `common.py`: bounded runtime helper
- `checklists/`: 外部 tool 採用前の確認項目
- `templates/`: 外部 tool 採用記録の雛形
- `roadmap/`: ADOP 整理 wave の記録
- `tasks/`: task board
- `design/`: bounded design notes
- `ADOP_SHELF_CLASSIFICATION.md`: common authority と project-local overlay の境界
- `ADOP_GENERIC_QUICKSTART.md`: generic ADOP の読み順と bounded verification path
- `REPO_EXPORT_GUIDE.md`: standalone repo へ抜く時の形
- `REPO_EXPORT_CHECKLIST.md`: standalone repo へ抜く前の確認
- `PRE_PUBLICATION_DECISIONS.md`: まだ未決の owner decision
- `CONTRIBUTING_DRAFT.md`: 公開前の contribution draft
- `SECURITY_DRAFT.md`: 公開前の security draft
- `RELEASE_BOOTSTRAP_NOTES.md`: 公開直前の bootstrap note
- `OWNER_DECISION_PACKET.md`: publishable hold から公開へ進むための owner decision packet
- `PUBLISHABLE_HOLD_CHECKLIST.md`: 公開可能保留状態の確認表
- `PUBLIC_GO_LIVE_SEQUENCE_DRAFT.md`: 実公開時の順序案
- `PUBLIC_POLICY_PROMOTION_MATRIX.md`: draft 文書を公開面へどう昇格させるか
- `PUBLIC_VERIFICATION_CONTRACT.md`: 公開前に必須の verification 面
- `PUBLICATION_RUNBOOK.md`: 実公開時の実行順序
- `PRIVATE_HOST_BOOTSTRAP_RUNBOOK.md`: private リポジトリ準備の実行順序
- `PRIVATE_RELEASE_HOLD_LINE.md`: private 準備後に止まる位置
- `SUPPORT.md`: issue 前の確認と問い合わせ導線

## 読み順

1. `README.md`
2. `ADOP_SHELF_CLASSIFICATION.md`
3. `ADOP_GENERIC_QUICKSTART.md`
4. `checklists/external-tool-adoption-checklist.md`
5. `templates/external-tool-adoption-note-template.md`
6. `python/adop_types.py`
7. `python/adop_cli.py`
8. `REPO_EXPORT_GUIDE.md`
9. `PUBLISHABLE_HOLD_CHECKLIST.md`
10. `OWNER_DECISION_PACKET.md`
11. `PUBLIC_POLICY_PROMOTION_MATRIX.md`
12. `PUBLIC_VERIFICATION_CONTRACT.md`
13. `PUBLICATION_RUNBOOK.md`
14. `PRIVATE_HOST_BOOTSTRAP_RUNBOOK.md`
15. `PRIVATE_RELEASE_HOLD_LINE.md`
16. `SUPPORT.md`

## 使い方

1. generic code と lifecycle を基準に project 側の runtime copy または overlay を保つ
2. `checklists/` を着手前に読む
3. `templates/` を project 側へ持ち込む
4. current trial、promote / hold / reject、operator 手順、landing target authority は project 側へ書く

## Standalone Repo View

- current physical home in this monorepo is `common/adop/`
- public-facing commands and file paths in this shelf are written repo-relative
- if this shelf is lifted into its own first public repo, use `REPO_EXPORT_GUIDE.md` as the carried-file authority
- extraction notes are in `REPO_EXPORT_GUIDE.md`

## Pre-Publication Drafts

The following are preparation assets only. They do not mean `ADOP` is already public.

- `PRE_PUBLICATION_DECISIONS.md`
- `CONTRIBUTING_DRAFT.md`
- `SECURITY_DRAFT.md`
- `RELEASE_BOOTSTRAP_NOTES.md`
- `OWNER_DECISION_PACKET.md`
- `PUBLISHABLE_HOLD_CHECKLIST.md`
- `PUBLIC_GO_LIVE_SEQUENCE_DRAFT.md`

## Publication Execution Docs

The following are execution-grade docs for getting from publishable hold to real publication. They are not themselves a claim that `ADOP` is already public.

- `PUBLIC_POLICY_PROMOTION_MATRIX.md`
- `PUBLIC_VERIFICATION_CONTRACT.md`
- `PUBLICATION_RUNBOOK.md`

## Private Bootstrap Docs

The following are execution-grade docs for preparing the repository in a private state while explicitly stopping before public release.

- `PRIVATE_HOST_BOOTSTRAP_RUNBOOK.md`
- `PRIVATE_RELEASE_HOLD_LINE.md`

## Repository Community Files

- `SUPPORT.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/CODEOWNERS`

## Common Authority が持つもの

- artifact schema
- trial lifecycle states
- bounded adoption CLI
- generic checklist
- generic adoption note template

## Project-Local Overlay が持つもの

- current trial board
- current summary
- operator flow
- hook / queue / runbook activation details
- landing target authority
- project-local decision log

## 書かないこと

- 特定 project の current trial board
- 特定 project の current summary
- project 固有の operator flow
- project 固有の judgment log
- project 固有の landing target authority

## 戻り先

- この棚の入口へ戻る: `README.md`
- standalone repo として読む時も、この `README.md` を起点にする
