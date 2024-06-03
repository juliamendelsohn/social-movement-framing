from transformers import AutoModel, AutoTokenizer, AutoModelForMaskedLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import load_dataset
import argparse
import os
os.environ["WANDB_DISABLED"] = "true"


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--train_data_file", default=None, type=str, required=True, help="The input training data file (a text file)."
    )
    parser.add_argument(
        "--eval_data_file", default=None, type=str, required=True, help="The input evaluation data file (a text file)."
    )
    parser.add_argument(
        "--output_dir",type=str,required=True, help="The output directory where the model predictions and checkpoints will be written.",
    )
    parser.add_argument(
        "--model_type", type=str, default='roberta-base', help="The model architecture to be trained or fine-tuned.",
    )
    parser.add_argument(
        "--num_train_epochs", default=3, type=float, help="Total number of training epochs to perform."
    )

    args = parser.parse_args()
    train_dataset = load_dataset('text', data_files=args.train_data_file, split='train')
    eval_dataset = load_dataset('text', data_files=args.eval_data_file, split='train')

    tokenizer = AutoTokenizer.from_pretrained('roberta-base')

    def preprocess_function(examples):
        return tokenizer([" ".join(x) for x in examples["text"]],truncation=True,padding='max_length',max_length=512)
    tokenized_train = train_dataset.map(preprocess_function, batched=True,num_proc=4)
    tokenized_eval = eval_dataset.map(preprocess_function, batched=True,num_proc=4)

    tokenizer.pad_token = tokenizer.eos_token
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm_probability=0.15)

    model = AutoModelForMaskedLM.from_pretrained(args.model_type)

    training_args = TrainingArguments(
        output_dir = args.output_dir,
        evaluation_strategy = 'epoch',
        save_strategy = 'epoch',
        num_train_epochs = args.num_train_epochs,
        load_best_model_at_end = True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        data_collator=data_collator,
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

if __name__ == "__main__":
    main()