# social-movement-framing
This repository contains materials for the Journal of Quantitative Description article _Framing Social Movements on Social Media: Unpacking Diagnostic, Prognostic, and Motivational Strategies_ (Mendelsohn, Vijan, Card, and Budak; 2024). The article is available open-access here: https://journalqd.org/article/view/5896

These materials include:
* Annotation Guidelines developed and used by annotators for data labeling
* Code for data collection, classification and analysis

* Please contact Julia Mendelsohn (juliame@umich.edu) for access to the annotated and full datasets. We are currently working on finding a way to share the datasets publicly and will update this page accordingly.

In addition, our RoBERTa models are publicly available through HuggingFace
* Relevance (binary classification)
    * Link: https://huggingface.co/juliamendelsohn/social-movement-relevance
* Stance (multiclass: conservative, neutral/unclear, progressive)
    * Link: https://huggingface.co/juliamendelsohn/social-movement-stance
* Core Framing Tasks (multilabel: diagnostic, prognostic, motivational)
    * Link: https://huggingface.co/juliamendelsohn/social-movement-core-framing-tasks
* Frame Elements (multilabel: problem id, blame, solutions, tactics, solidarity, counterframing, motivational)
    * Link: https://huggingface.co/juliamendelsohn/social-movement-framing-elements

Check out [this Colab Notebook](https://colab.research.google.com/drive/16WEkvRaEQ7hugQByVVrwfUTJm-2Aiv-S) for how to download and make predictions with these models using SimpleTransformers.



Please cite as follows:

Mendelsohn, J., Vijan, M., Card, D., & Budak, C. (2024). Framing Social Movements on Social Media: Unpacking Diagnostic, Prognostic, and Motivational Strategies. Journal of Quantitative Description: Digital Media, 4.

```
@article{mendelsohn2024framing,
  title={Framing Social Movements on Social Media: Unpacking Diagnostic, Prognostic, and Motivational Strategies},
  author={Mendelsohn, Julia and Vijan, Maya and Card, Dallas and Budak, Ceren},
  journal={Journal of Quantitative Description: Digital Media},
  volume={4},
  year={2024}
}
```
