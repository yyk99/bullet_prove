# DVC Setup

[DVC](https://dvc.org) is used to version and share binary assets that are too
large for git: real target photos (`data2/`, `data3/`) and trained model
checkpoints (`checkpoints/`). Git stores small `.dvc` pointer files; the actual
data lives in S3.

## Install

```bash
pip install "dvc[s3]"
```

The `[s3]` extra pulls in `boto3` for AWS S3 access. If you installed the
project dependencies via `pip install -r requirements.txt` first, only the
`dvc[s3]` package is needed on top.

## AWS credentials

DVC uses the standard AWS credential chain. Any of the following works:

**Option A — AWS credentials file** (recommended for local dev)

```bash
aws configure   # requires the AWS CLI
```

This writes `~/.aws/credentials`. If you don't have the AWS CLI, create the
file manually:

```ini
[default]
aws_access_key_id     = AKIA...
aws_secret_access_key = ...
region                = us-east-1
```

**Option B — environment variables**

```bash
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1
```

**Option C — DVC local config** (credentials stay on this machine, never committed)

```bash
dvc remote modify --local s3remote access_key_id AKIA...
dvc remote modify --local s3remote secret_access_key ...
```

## Download data (after cloning)

```bash
dvc pull
```

This fetches `data2/`, `data3/`, and `checkpoints/` from S3.

## Upload new or changed data

```bash
dvc add data2/          # update the pointer file after adding new images
git add data2.dvc
git commit -m "Add new target photos"
dvc push                # upload to S3
git push
```

## Remote configuration

The default remote is `s3remote`:

```
s3://bullet-prove-data-490954040359-us-east-1-an/bullet-prove/
```

See `.dvc/config` for the full configuration.
