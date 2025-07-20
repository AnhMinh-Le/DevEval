ROOT=/home/user/DevEval
TASK=without_context
Model=gpt-4-1106-preview_greedy

python $ROOT/check_source_code.py $ROOT/Source_Code

# Compute Pass@1
python pass_k.py \
    --output_file $ROOT/Experiments/$TASK/$Model/completion.jsonl \
    --log_file $ROOT/Experiments/$TASK/$Model/test_output.jsonl \
    --source_code_root $ROOT/Source_Code \
    --data_file $ROOT/data.jsonl \
    --n 1 \
    --k 1

Model=gpt-4-1106-preview

python $ROOT/check_source_code.py $ROOT/Source_Code

# Compute Pass@3,5,10
python pass_k.py \
    --output_file $ROOT/Experiments/$TASK/$Model/completion.jsonl \
    --log_file $ROOT/Experiments/$TASK/$Model/test_output.jsonl \
    --source_code_root $ROOT/Source_Code \
    --data_file $ROOT/data.jsonl \
    --n 20 \
    --k 3,5,10

python pass_k.py \
    --output_file /mnt/d/ReFunc/Eval/DevEval/data/deveval/Qwen2.5-Coder-1.5B-Instruct-base/deveval.final.generated.jsonl \
    --log_file /mnt/d/ReFunc/Eval/DevEval/data/deveval/Qwen2.5-Coder-1.5B-Instruct-base/test_output.jsonl \
    --source_code_root /mnt/d/ReFunc/Eval/DevEval/Source_Code \
    --data_file /mnt/d/ReFunc/Eval/DevEval/data.jsonl \
    --n 5 \
    --k 1,3,5


python pass_k.py \
    --output_file /mnt/d/ReFunc/Eval/DevEval/data/deveval/Qwen2.5-Coder-1.5B-Instruct-custom_bm25/deveval.final.generated.jsonl \
    --log_file /mnt/d/ReFunc/Eval/DevEval/data/deveval/Qwen2.5-Coder-1.5B-Instruct-custom_bm25/test_output.jsonl \
    --source_code_root /mnt/d/ReFunc/Eval/DevEval/Source_Code \
    --data_file /mnt/d/ReFunc/Eval/DevEval/data.jsonl \
    --n 5 \
    --k 1,3,5


python pass_k.py \
    --output_file /mnt/d/ReFunc/Eval/DevEval/data/deveval/Qwen2.5-Coder-1.5B-Instruct-bm25/deveval.final.generated.jsonl \
    --log_file /mnt/d/ReFunc/Eval/DevEval/data/deveval/Qwen2.5-Coder-1.5B-Instruct-bm25/test_output.jsonl \
    --source_code_root /mnt/d/ReFunc/Eval/DevEval/Source_Code \
    --data_file /mnt/d/ReFunc/Eval/DevEval/data.jsonl \
    --n 5 \
    --k 1,3,5


