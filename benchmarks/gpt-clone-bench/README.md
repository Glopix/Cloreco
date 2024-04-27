# GPTCloneBench
GPTCloneBench is a clone detection benchmark based on SemanticCloneBench [1] and GPT [2,3,4,5]. This work is accepted at ICSME2023 conference.

GitHub URL: [GPTCloneBench GitHub](https://github.com/srlabUsask/GptCloneBench/)

arXiv link of Paper: [GPTCloneBench arXiv](https://arxiv.org/pdf/2308.13963.pdf)

Full version of Benchmark: [Zenodo version 2] (https://doi.org/10.5281/zenodo.10198952)

Last Updated: 22-November-2023

## Summary
GPTCloneBench consists of Moderate Type-3 with 5% gray area (similarity range 50% to 75%) and Type-4 (similarity range 0% to 50%).

To create this benchmark, we have used GPT-3 (text-da-vinci model) and SemanticCloneBench. We have used Few-shot Prompt Engineering technique. Our two selected prompts are given in the main paper.


## Folder Structure

GPTCloneBench folder structure is given below. We have divided into two main folders: injected_clones and standalone.In this version only standalone clones are given and in standalone folder, every clone pair is given in a seperate file. We encourge users to utilize both of the system and report any update they would like to see.

```
|__GPTCloneBench

    |__standalone
        |__false_semantic_clones (Type-1 and Type-2 clones are here)
        |__true_semantic_clones (MT3+5% gray area and T4 clones are here)
            |__c (only c clones)
                |__prompt_1 (clones after running first prompt)
                    |__MT3 (Moderate Type-3 + 5% gray area clones are here)
                    |__T4 (Type-4 clones are here)
                |__prompt_2 (clones after running second prompt)
                    |__MT3 (Moderate Type-3 + 5% gray area clones are here)
                    |__T4 (Type-4 clones are here)
            |__cs (only c-sharp clones)
                |__prompt_1 (clones after running first prompt)
                    |__MT3 (Moderate Type-3 + 5% gray area clones are here)
                    |__T4 (Type-4 clones are here)
                |__prompt_2 (clones after running second prompt)
                    |__MT3 (Moderate Type-3 + 5% gray area clones are here)
                    |__T4 (Type-4 clones are here)
            |__java (only java clones)
                |__prompt_1 (clones after running first prompt)
                    |__MT3 (Moderate Type-3 + 5% gray area clones are here)
                    |__T4 (Type-4 clones are here)
                |__prompt_2 (clones after running second prompt)
                    |__MT3 (Moderate Type-3 + 5% gray area clones are here)
                    |__T4 (Type-4 clones are here)
            |__py (only python clones)
                |__prompt_1 (clones after running first prompt)
                    |__MT3 (Moderate Type-3 + 5% gray area clones are here)
                    |__T4 (Type-4 clones are here)
                |__prompt_2 (clones after running second prompt)
                    |__MT3 (Moderate Type-3 + 5% gray area clones are here)
                    |__T4 (Type-4 clones are here)

```


## BibTeX Citation
```
1. @inproceedings{al2020semanticclonebench,
    title={Semanticclonebench: A semantic code clone benchmark using crowd-source knowledge},
    author={Al-Omari, Farouq and Roy, Chanchal K and Chen, Tonghao},
    booktitle={2020 IEEE 14th International Workshop on Software Clones (IWSC)},
    pages={57--63},
    year={2020},
    organization={IEEE}
  }

2. @article{brown2020language,
    title={Language models are few-shot learners},
    author={Brown, Tom and Mann, Benjamin and Ryder, Nick and Subbiah, Melanie and Kaplan, Jared D and Dhariwal, Prafulla and Neelakantan, Arvind and Shyam, Pranav and Sastry, Girish and Askell, Amanda and others},
    journal={Advances in neural information processing systems},
    volume={33},
    pages={1877--1901},
    year={2020}
}

3. @misc{morrison_2022, 
    title={GPT-3 developer OpenAI releases new Davinci Generative Text Model}, 
    url={https://techmonitor.ai/technology/ai-and-automation/gpt-3-openai-davinci-generative-text}, 
    journal={Tech Monitor}, 
    author={Morrison, Ryan}, 
    year={2022}, 
    month={Nov}
 }

4. @misc{jain_2022,
    title={OpenAI turns to Davinci to make GPT-3 Better},
    url={https://analyticsindiamag.com/openai-turns-to-davinci-to-make-gpt-3-better/},
    journal={Analytics India Magazine},
    author={Jain, Ayush},
    year={2022},
    month={Nov}
} 

5. @misc{monge_2022,
    title={New GPT-3 model: Text-DAVINCI-003 is awesome},
    url={https://medium.com/technology-hits/new-gpt-3-model-text-davinci-003-is-awesome-ada11ef660a9},
    journal={Medium},
    publisher={Technology Hits},
    author={Monge, Jim Clyde},
    year={2022},
    month={Dec}
} 
```