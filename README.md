# README

> **Note:** This readme template is based on one from the [Good Docs Project](https://thegooddocsproject.dev). You can find it and a guide to filling it out [here](https://gitlab.com/tgdp/templates/-/tree/main/readme). (_Erase this note after filling out the readme._)

<h1 align="center">
  <br>
  <a href="https://openpecha.org"><img src="https://avatars.githubusercontent.com/u/82142807?s=400&u=19e108a15566f3a1449bafb03b8dd706a72aebcd&v=4" alt="OpenPecha" width="150"></a>
  <br>
</h1>

## _Pecha Uploader_

## Owner(s)
- [@sandup](https://github.com/lobsam)


## Table of contents
<p align="center">
  <a href="#project-description">Project description</a> •
  <a href="#who-this-project-is-for">Who this project is for</a> •
  <a href="#project-dependencies">Project dependencies</a> •
  <a href="#instructions-for-use">Instructions for use</a> •
  <a href="#contributing-guidelines">Contributing guidelines</a> •
  <a href="#additional-documentation">Additional documentation</a> •
  <a href="#how-to-get-help">How to get help</a> •
  <a href="#terms-of-use">Terms of use</a>
</p>
<hr>

## Project description
_This package is used for uploading Pechas(JSON format) to pecha.org via Sefaria platform._

## Who this project is for
This project is intended for _Data Engineers_ who wants  to _upload pechas to our pecha.org website_.

## Project dependencies
Before using _Project Name_, ensure you have:
* python _version 3.8 >=_
* _Network Connection_
* _PECHA_API_KEY(ask from owner)_


## Instructions for use


### _Install_
```python
pip install git+https://github.com/OpenPecha/pecha_uploader.git
```
### _Destination url/Server url_
we have three servers:
```
* Destination_url.STAGING
* Destination_url.PRODUCTION
* Destination_url.LOCAL
```


### _Run_
```python
from pathlib import Path
from pecha_uploader.pipeline import upload_root, upload_commentary, upload
from pecha_uploader.config import Destination_url


root_pecha_path = Path("path/to/root/pecha")
upload_root(root_pecha_path)


commentary_pecha_path = Path("path/to/commentary/pecha")
upload_commentary(commentary_pecha_path)


pecha_path = Path("path/to/pecha") # Root or Commentary Pecha
upload(pecha_path)
```

### _Overwrite Run_

```python
from pathlib import Path
from pecha_uploader.pipeline import upload_root, upload_commentary
from pecha_uploader.config import Destination_url

root_pecha_path = Path("path/to/root/pecha")
upload_root(root_pecha_path, Destination_url.STAGING, overwrite=True)


commentary_pecha_path = Path("path/to/commentary/pecha")
upload_commentary(commentary_pecha_path, Destination_url.STAGING, overwrite=True)


pecha_path = Path("path/to/pecha") # Root or Commentary Pecha
upload(pecha_path, Destination_url.STAGING, overwrite=True)

```

### _Troubleshoot_
_In your home directory, there would be a folder named `.pecha_uploader`.And regarding when uploading
the pechas.If you go inside inner folder called `texts`.There would be three .txt files._

1. `success.txt` : This file contains the list of pechas that are successfully uploaded.
2. `errors.txt` : This file contains the list of pechas that are failed to upload with error description.
3. `error_ids.txt`: This file contains the list of pechas that are failed to upload with pecha id.


## Contributing guidelines
If you'd like to help out, check out our [contributing guidelines](/CONTRIBUTING.md).


## Additional documentation
_Include links and brief descriptions to additional documentation._

For more information:
* [Reference link 1](#)
* [Reference link 2](#)
* [Reference link 3](#)


## How to get help
* File an issue.
* Email us at openpecha[at]gmail.com.
* Join our [discord](https://discord.com/invite/7GFpPFSTeA).


## Terms of use
_Project Name_ is licensed under the [MIT License](/LICENSE.md).
