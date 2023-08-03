eps=0.2
########################################################################################
for minority in 3
do
    for d in 0.3
    do
        for penalty in 2.0
        do
            for formulation in "imbalance-fl-res"
            do
                for eta_dual in 0.1 0.5 1.0 2.0
                do
                    for eta_resilient in 0.1 0.5 1.0
                    do
                    python run_PD_FL.py --perturbation_penalty $penalty --perturbation_lr $eta_resilient --project FedResFinal --imbalance --dataset cifar10 --n_workers_per_round 100 --reduce_to_ratio .1 --use_ray --formulation $formulation --learner fed-avg --local_lr 1e-1 --n_pd_rounds 1000 --loss_fn cross-entropy-loss --model convnet --n_workers 100 --n_p_steps 5 --lambda_lr $eta_dual --tolerance_epsilon ${eps} --use_gradient_clip --n_minority 3 --run penalty_abl_${penalty} --heterogeneity dir --dir_level 0.3
                    done
                done
            done
        done
    done
done