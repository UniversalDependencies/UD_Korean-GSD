# Documentation
by Jayeol Chun | Apr 8

Provides a brief overview of fixed annotation's current status. It does not attempt to be comprehensive at this point of writing.

### Notable Issues / Concerns
1. Tokenization
  * okay
2. Mislabeled POS / dependency labels
  * these were *not touched* unless they were part of splitted morphemes as a result of new tokenization
    * As a result, there might be inconsistency in notation between the new annotation and the original. The original one seems to be mixing UD version 1.0 and 2.0 tag/label notation. I strictly adhered to 2.0.
    * Of particular interest is the *secondary POS tag* that only exists in the original version. They were helpful in inferring dependency labels, but it's questionable whether they should be retained in the final product. They were retained unless I derived entirely new POS tag from the original.

3. Important notes/decisions I made
  * While pos tags were aggressively fixed and newly annotated, I chose to *inherit the original labels* as much as possible, just to ensure that I do not introduce a new error into the data.
  * Inside of the Parenthesis was given the dependency label *appos* rather than parataxis. Read [here](http://universaldependencies.org/u/dep/appos.html). Due to multi-word expressions inside the parenthesis, multiple appos labels might exist, where they should only be one from the head of that inner expression. *dev-s2* below is one example.
  * Two subtlest cases:
    1. Ending quotation mark
    ```
    dev-s513
    -prev-
      21	중요하다"며	_	VERB	PREDCONJ	_	30	advcl	_	_	중요/XR+하/XSA+다/EC+"/SS+며/EC
    -after-
      22	중요하다	_	ADJ	ADJ	_	36	amod	_	SpaceAfter=No	중요/XR+하/XSA+다/EC
      23	"	_	PUNCT	.	_	22	punct	_	SpaceAfter=No	"/SS
      24	며	_	ADP	ADP	_	22	case	_	_	며/EC
    ```
    While many of these constructions follow the above example, there are some such as the example below:
    ```
    test-s762
    -prev-
      10	야구'다.	_	VERB	NOMCOP	_	0	root	_	_	야구/NNG+'/SS+이/VCP+다/EF+./SF
    -after-
      11	야구	_	NOUN	NOUN	_	13	dep	_	SpaceAfter=No	야구/NNG
      12	'	_	PUNCT	.	_	11	punct	_	SpaceAfter=No	'/SS
      13	다	_	VERB	NOMCOP	_	0	root	_	SpaceAfter=No	이/VCP+다/EF
      14	.	_	PUNCT	.	_	13	punct	_	_	./SF
    ```
    I am not entirely sure whether 중요하다 should be the dependent of 며 in the first example. In much the same vein of uncertainty, I am not sure whether 야구 should have been the root in the second example, although the current version does look correct.
    Also, note that 야구 has *dep* as its label: I am still trying to see whether it's possible to deterministically determine the relationship in cases like this. In cases where the uncertainty could not be confidently resolved, I inherited the original dependency label, only using *dep* where context did not make sense, i.e. POS-tag is *NOUN* and dependency label is *amod*.

    2. Fully embedded Parenthesis
      * Case 1 : No space in between
      ```
      test-s173
      -prev-
        3	미륵불(彌勒佛)이라	_	VERB	PREDCOMP	_	4	ccomp	_	_	미륵불/NNG+(/SS+彌勒佛/SH+)/SS+이/VCP+라/EC
      -after-
        3	미륵불	_	NOUN	NOUN	_	8	ccomp	_	SpaceAfter=No	미륵불/NNG
        4	(	_	PUNCT	.	_	5	punct	_	SpaceAfter=No	(/SS
        5	彌勒佛	_	SYM	SYM	_	3	appos	_	SpaceAfter=No	彌勒佛/SH
        6	)	_	PUNCT	.	_	5	punct	_	SpaceAfter=No	)/SS
        7	이라	_	VERB	PREDCOMP	_	3	ccomp	_	_	이/VCP+라/EC
      ```
      Similarly, it seems reasonable to have 이라 to be the head of 미륵불.

      * Case 2 : Spaces in between
      ```
      test-s187
      -prev-
      30	달러(약	_	NOUN	NOUN	_	28	flat	_	_	달러/NNB+(/SS+약/MM
      31	4억	_	NUM	NUM	NumType=Card	28	nummod	_	_	4/SN+억/NR
      32	3천만	_	NUM	NUM	NumType=Card	28	nummod	_	_	3/SN+천만/NR
      33	원)의	_	NOUN	NOUN	_	28	flat	_	_	원/NNB+)/SS+의/JKG
      -after-
      30	달러	_	NOUN	NOUN	_	28	flat	_	SpaceAfter=No	달러/NNB
      31	(	_	PUNCT	.	_	32	punct	_	SpaceAfter=No	(/SS
      32	약	_	DET	DET	_	30	appos	_	_	약/MM
      33	4억	_	NUM	NUM	NumType=Card	28	nummod	_	_	4/SN+억/NR
      34	3천만	_	NUM	NUM	NumType=Card	28	nummod	_	_	3/SN+천만/NR
      35	원	_	NOUN	NOUN	_	28	appos	_	SpaceAfter=No	원/NNB
      36	)	_	PUNCT	.	_	35	punct	_	SpaceAfter=No	)/SS
      37	의	_	ADP	ADP	_	28	case	_	_	의/JKG
      ```
      While the leftmost and rightmost elements within the parenthesis are given *appos* label, middle elements like 4억 and 3천만 are not touched, thus retaining their original information.

4. Heuristics
  * The exact heuristics used to derive POS tags and dependency labels have not been prepared for documentation, mainly because it is undergoing daily changes with newly encountered exceptional cases. But they will be ready for inspection soon.

### Miscellaneous Notes
1. Embedded punctuations were combined with appropriate neighboring morphemes.
  * ex 1) Numbers with ',' and '.' in the middle, denoting a large number or a decimal
  ```
  dev-s914
  -prev-
    4	7.6~26.9	_	NOUN	NUMNOUN	_	0	root	_	_	7/SN+./SF+6/SN+~/SO+26/SN+./SF+9/SN
    5	%,	_	PUNCT	.	_	4	punct	_	_	%/SW+,/SP
  -after-
    4	7.6	_	NUM	NUM	_	0	nummod	_	SpaceAfter=No	7.6/SN
    5	~	_	SYM	.	_	4	punct	_	SpaceAfter=No	~/SO
    6	26.9	_	NUM	NUM	_	0	nummod	_	_	26.9/SN
    7	%	_	SYM	.	_	6	punct	_	SpaceAfter=No	%/SW
  ```
  * ex 2) Ampersands
  ```
  dev-s184
  -prev-
    8	토크&라이브'	_	NOUN	PNOUN	_	7	flat	_	SpaceAfter=No	토크/NNG+&/SW+라이브/NNG+'/SS
  -after-
    9	토크&라이브	_	NOUN	NOUN	_	8	flat	_	SpaceAfter=No	토크&라이브/NNG
    10	'	_	PUNCT	.	_	9	punct	_	SpaceAfter=No	'/SS
  ```
  * ex 3) URLs (some alphabets were being recognized as punctuations)
  ```
  dev-s2
  -prev-
    6	경기국제의료관광협의회(e-gima.com)가	_	NOUN	PNOUN	_	5	conj	_	_	경기/NNG+국제/NNG+의료/NNG+관광/NNG+협의회/NNG+(/SS+e/SL+-/SS+g/SW+i/SL+m/SW+a/SL+./SF+com/SL+)/SS+가/JKS
  -after-
    6	경기국제의료관광협의회	_	PROPN	PROPN	_	5	conj	_	SpaceAfter=No	경기/NNG+국제/NNG+의료/NNG+관광/NNG+협의회/NNG
    7	(	_	PUNCT	.	_	8	punct	_	SpaceAfter=No	(/SS
    8	e-gima.com	_	NOUN	NOUN	_	6	appos	_	SpaceAfter=No	e-gima.com/SL
    9	)	_	PUNCT	.	_	8	punct	_	SpaceAfter=No	)/SS
    10	가	_	ADP	ADP	_	6	case	_	_	가/JKS
  ```
  * ex 4) Embedded hyphens
  ```
  dev-s132
  -prev-
    8	AFC-CONCACAF	_	NOUN	PNOUN	_	5	flat	_	_	AFC/SL+-/SS+CONCACAF/SL
  -after-
    8	AFC-CONCACAF	_	NOUN	PNOUN	_	5	flat	_	_	AFC-CONCACAF/SL
  ```
2. Splitted punctuations point to the token before it. But they point to the token *after* it if:
  1. it is one of *"<", "《", "(", "[", "$"*
  ```
  dev-s430
  -prev-
    2	부락제(部落祭)는	_	NOUN	NOUN	_	17	nsubj	_	_	부락제/NNG+(/SS+部落祭/SH+)/SS+는/JX
  -after-
    2	부락제	_	NOUN	NOUN	_	47	nsubj	_	SpaceAfter=No	부락제/NNG
    3	(	_	PUNCT	.	_	4	punct	_	SpaceAfter=No	(/SS
    4	部落祭	_	SYM	SYM	_	2	appos	_	SpaceAfter=No	部落祭/SH
    5	)	_	PUNCT	.	_	4	punct	_	SpaceAfter=No	)/SS
  ```
  2. it is one of *'\"', '\'', '`'* and its previous token has 'SpaceAfter=No' feature.
  ```
  dev-s513
  -prev-
    3	"빈곤	_	NOUN	NOUN	_	5	advmod	_	_	"/SS+빈곤/NNG
  -after-
    3	"	_	PUNCT	.	_	4	punct	_	SpaceAfter=No	"/SS
    4	빈곤	_	NOUN	NOUN	_	6	advmod	_	_	빈곤/NNG
  ```
2. Empty parenthesis was handled to avoid cycles:
  ```
  dev-s311
  -prev-
    2	위키백과()는	_	NOUN	NOUN	_	1	flat	_	_	위키/NNP+백과/NNG+(/SS+)/SS+는/JX
  -after-
    2	위키백과	_	NOUN	NOUN	_	1	flat	_	SpaceAfter=No	위키/NNP+백과/NNG
    3	(	_	PUNCT	.	_	4	punct	_	SpaceAfter=No	(/SS
    4	)	_	PUNCT	.	_	2	punct	_	SpaceAfter=No	)/SS
  ```
3. Traditional Chinese characters were recognized as 'SYM', while English was read as 'NOUN' most of the time.
