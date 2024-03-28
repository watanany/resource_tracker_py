# Snowflake を Terraform 化

- ① [Snowflake provider のドキュメント](https://github.com/Snowflake-Labs/terraform-provider-snowflake/tree/main/docs/resources)をスクレイピング
- ② ①の結果を元に Python のクラスを生成
- ③ ②の結果と SQL で Terraform のコードを生成

## 使い方

``` shell
$ pyenv install
$ poetry install

$ # .env.sample を元に Snowflake 用に環境変数を設定する
$ cp .env.sample .env

$ # ①
$ poetry run python apps/fetch_resource_schemas.py > data/resources.jsonl 

$ # ②
$ poetry run python apps/generate_resource_schemas.py
$ # 生成結果を resource_tracker/types.py に入れる

$ # ③
$ poetry run python apps/render_resources.py
$ # outputs に.tf ファイルと import.sh が生成される
```
