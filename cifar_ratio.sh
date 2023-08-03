DEVICE=0
imbalance=0.1
########################################################################################
for minority in 1 3
do
    for d in 0.3 10.0
    do
        for eps in 0.1
        do
            for formulation in "ratioloss-fl"
            do
                python run_PD_FL.py --perturbation_penalty 2 --project FedResFinal --imbalance --dataset cifar10 --n_workers_per_round 100 --reduce_to_ratio $imbalance --use_ray --formulation $formulation --learner fed-avg --local_lr 1e-1 --n_pd_rounds 1000 --loss_fn cross-entropy-loss --model convnet --n_workers 100 --n_p_steps 5 --lambda_lr 2 --tolerance_epsilon ${eps} --use_gradient_clip --n_minority $minority --run abl_minority_$minority --heterogeneity dir --dir_level $d
            done
        done
    done
done
#CUDA_VISIBLE_DEVICES=$DEVICE