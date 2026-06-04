# External Tool Adoption Checklist

**使う場面**: 新しい外部 tool を試す前や、運用へ組み込むかを決める時に使う。  
**差し替える所**: tool 名、採用 class、判断者、試行手順。  
**書かないこと**: 外部 tool 採用 note 本文、今の状態の正本、project 固有の current 運用。

**目的**: 外部 tool / tracker / memory / workflow helper を、ad-hoc な便利使いではなく、project の運用組込または基盤作成補助として安全に採るための共通 checklist。

**共通棚として持つもの**: generic な判断観点だけ。  
**project 側へ出すもの**: current state、landing target authority、operator flow、project 固有 trigger detail。

## 補足

- 新しい外部 tool を試す前
- 既存 external tool を繰り返し使い始めた時
- `運用組込` へ昇格させるか、`作成補助` のまま保つかを決める時

## 1. 先に分類する

- `運用組込` か `作成補助` かを先に決めた
- `interface / mechanism / scaling` のどの harness layer を強くするか書ける
- `core build / future extension / implementation / self-improvement loop` のどの phase か書ける

## 2. 運用組込として採る場合

- trigger / hook / runbook / healthcheck / queue のどこで使うか決めた
- authority を何に置くか決めた
- authority にしないものを明記した
- fail-close / escalation / verification を決めた
- current canonical surface から「どの場面で自動または半自動で使うか」を辿れる

## 3. 作成補助として採る場合

- いつ使うか決めた
- 何のために使うか決めた
- tool の output 自体は SSOT ではないと明記した
- repo 正本へ何を落とすか決めた
- 単発利用か、反復利用かを切った

## 4. 反復利用時の昇格

- 反復利用なら `workflow / checklist / skill / hook / runbook` のどれへ昇格するか決めた
- 昇格しないなら、なぜ単発支援で止めるか説明できる
- `便利だから毎回使う` 状態を残していない

## 5. current 判定メモ

current candidate reading を残す場合は、対象 project の current state と date を明記する。

- `運用組込` / `作成補助` の current state を明記した
- 強くする層を `interface / mechanism / scaling` から選んだ
- current approved use scenes を対象 project に即して書ける
- current prohibited scenes を対象 project に即して書ける
- project 固有の current canonical surface を、共通 checklist 本文へ直書きしない

## 6. completion artifact

外部 tool を採る時は、最低限次のどれかを repo に残す。

- adoption note
- trial board row
- workflow / runbook update
- checklist / template
- hook / healthcheck / queue integration

artifact が残らないなら、採用は完了扱いにしない。

## 7. trial lifecycle

- `proposed / trial-ready / in-trial / promote / hold / reject` のどこにいるかを current canonical に残した
- `landing_target` を machine-readable に固定し、promote 後の書き戻し先を trial 開始前に決めた
- executor / trigger / evaluation gate / decision owner / current state を machine-readable に持った
- start 時に scene と評価観点を固定した
- close 時に artifact / observed effect / next action を残した
