# Web-Record-Extraction-with-Invariants
This repo hosts the code base for our paper "[Web-Record-Extraction-with-Invariants]()", which presents a method to extract complex **list-like** Web records that have significant structural variations due to heterogeneous schema or hierarchically nesting structures.

## Setup
Create a Python virtual environment and install requirements.

`
pip install -r requirements.txt
`
## Usage
Use the following command to extract Web records from local HTML files:

`
python run.py <input> [--output=output.html] [--encoding=structure] [--len-thresh=3] [--freq-thresh=3] [--record-height-thresh=2] [--record-size-thresh=3]
`

Where

`input`: the input HTML file for Web record extraction.

`--output`: the output HTML file with results stored in element attributes, default to "output.html".

`--encoding`: the encoding scheme for nodes on the DOM tree, should be one of "tag" (encode by tag name), "signature" (encode by node signature), "htp" (encode by HTML Tag Path), and "structure" (encode by subtree structure). Defaults to "structure".

`--len-thresh`: pattern length threshold for the invariant structures, defaults to 3.

`--freq-thresh`: pattern frequency threshold, defaults to 3.

`--record-height-thresh`: subtree height threshold of output records, defaults to 2.

`--record-size-thresh`: subtree size threshold of output records, defaults to 3.

The repository contains three input examples of different types of Web records, including [amazon.html](amazon.html) (search results page from Amazon), [google.html](google.html) (search results page from Google), and [comments.html](comments.html) (a comment section from Fox News, the comment contents and user names are masked out).

Use the following command to run with the examples:

`
python run.py amazon.html --output=amazon-output.html --len-thresh=5 --freq-thresh=5
`

`
python run.py google.html --output=google-output.html --len-thresh=5 --freq-thresh=5
`

`
python run.py comments.html --output=comments-output.html --len-thresh=5 --freq-thresh=5
`



The results are stored as attributes in the output html file. Each record container node is labelled by the attribute `data-record-boundary`, and we also highlight the record container elements with dashed green rectangles so one may open the output file in the browser to examine the results.

One may adjust the pattern length threshold and pattern frequency threshold to fine-tune the output. Below are a few suggestions for adjusting the parameters:

1. Adjust the pattern length threshold according to the size of the target Web record, i.e., the size of the subtree containing the record. Larger Web records should have higher pattern length threshold.
2. Adjust the pattern frequency threshold according to the number of the target Web records. Choose a higher threshold if there are more target Web records. 
3. If there is no prior knowledge about the target records, set both to 3 (default value).

## Evaluate
To evaluate the method, one needs to supplement the XPath that returns the elements of the ground truth record container nodes. For example, use the following command to run evaluation on the included examples:

`
python run.py amazon.html --output=amazon-output.html --len-thresh=5 --freq-thresh=5 --evaluate-xpath="//div[contains(@class, 'sg-col-4-of-12') and contains(@class, 's-result-item')]"
`

`
python run.py google.html --output=google-output.html --len-thresh=5 --freq-thresh=5 --evaluate-xpath="//div[./div/div/div/a[./h3 and ./div/cite]]"
`

`
python run.py comments.html --output=comments-output.html --len-thresh=5 --freq-thresh=5 --evaluate-xpath="//li"
`

In the output file, we use `data-record-hit` attribute to label the true positives , `data-record-mistake` for false positives, and `data-record-miss` for false negatives. Their boundaries are also highlighted by green, yellow and red, respectively.

## Datasets
Here are the instructions to run the method on the 5 datasets described in the paper.
1. To test the method on the TBDW dataset, download the datatset [here](https://drive.google.com/file/d/16x6_oyB1NhUP4leUSR1PKpKcH9oM2_CU/view?usp=sharing), and run the method with the reference XPaths that we manually composed for each of the websites, which is available in [TBDW-xpath.json](TBDW-xpath.json). You may use the utility function `read_TBDW_xpath` in [xpath_reader.py](xpath_reader.py) to quey the corresponding XPath for each sample.

2. To test the method on the EX data set, download and combine the EX1 and EX2 dataset [here](https://app.box.com/s/vi4c976afptq39524y1pofz7fw995qf9), and run the method with the reference XPaths that we manually composed for each of the websites, which is available in [EX-xpath.json](EX-xpath.json). You may use the utility function `read_EX_xpath` in [xpath_reader.py](xpath_reader.py) to quey the corresponding XPath for each sample.

3. To test the method on the AMAZON data set, download the dataset [here](https://drive.google.com/file/d/17AZQ3areODpVw6ENuNIyVyIguDiVP5t2/view?usp=sharing), and run the method with the following XPath: 
   
   `--evaluate-xpath="//div[contains(@class, 's-result-item') and .//span[contains(text(), '$')] and not(.//div[contains(@class, 's-result-item')]) and not(.//li[@class='a-carousel-card'])]|//li[@class='a-carousel-card']"`

4. To test the method on the GOOGLE dataset, download the datatset [here](https://drive.google.com/file/d/1eRvUrE10x57niH6Po0S38Fz3-VqoM6Re/view?usp=sharing), and run the method with the following parameters:

    `--evaluate-xpath="//div[./div/div/div/a[./h3 and ./div/cite]]"`

    `--len-thresh=5`

    `--freq-thresh=5`

5. We are not allowed to share the COMMENT dataset, but we provide a list of websites where the comments are collected in [websites-with-comments.txt](websites-with-comments.txt). We suggest using [Selenium](https://www.selenium.dev/) to automate the data collection process so the webpages are rendered to fully present the structural complexity of comments.