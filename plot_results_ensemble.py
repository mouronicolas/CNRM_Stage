import os
import argparse
import core.logger as logger
import pandas as pd
import numpy as np

import ensemble.load_data as lde
import ensemble.maps as maps
import ensemble.stats as stats

import warnings
warnings.filterwarnings("ignore")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, default='config/sr_example.jsonc',
                        help='JSON file for configuration')
    parser.add_argument('-gpu', '--gpu_ids', type=str, default=None)

    # parse configs
    args = parser.parse_args()
    opt = logger.parse(args)

    # create dirs
    for _, item in opt["path"].items():
        os.makedirs(item, exist_ok=True)

    ens_opt_arome = opt["ensemble"]["Arome"]
    ens_opt_ddpm  = opt["ensemble"]["DDPM"]

    # load ensembles
    arome_ensemble = lde.load_ensemble_arome(
        dates=ens_opt_arome["dates"],
        echeances=ens_opt_arome["echeances"],
        params=opt["data_loading"]["params_out"],
        n_members=ens_opt_arome["n_members"],
        data_location=ens_opt_arome["data_location"]
    )
    arome_ensemble = lde.correct_dates_for_arome(arome_ensemble)
    arome_ensemble = lde.add_input_output(
        arome_ensemble,
        opt["data_loading"]["interp"],
        opt["data_loading"]["data_test_location"],
        opt["data_loading"]["params_out"]
    )

    ddpm_ensemble = lde.load_ensemble_ddpm(
        working_dir=opt["path"]["working_dir"],
        n_members=ens_opt_ddpm["n_members"],
        params=opt["data_loading"]["params_out"]
    )
    ddpm_ensemble = lde.add_input_output(
        ddpm_ensemble,
        opt["data_loading"]["interp"],
        opt["data_loading"]["data_test_location"],
        opt["data_loading"]["params_out"]
    )

    # for i_p, p in enumerate(opt["data_loading"]["params_out"]):

    #     output_dir = os.path.join(opt["path"]["working_dir"], p + "/")
    #     os.makedirs(output_dir, exist_ok=True)
    #     output_dir_arome = os.path.join(output_dir, "arome/")
    #     os.makedirs(output_dir_arome, exist_ok=True)
    #     output_dir_ddpm = os.path.join(output_dir, "ddpm/")
    #     os.makedirs(output_dir_ddpm, exist_ok=True)
        

    #     # plot maps for all ensembles
    #     print("plotting maps ...")
    #     maps.plot_maps_ensemble(
    #         arome_ensemble,
    #         output_dir_arome,
    #         param=p,
    #         n_members=ens_opt_arome["n_members"],
    #         n=opt["results"]["images"]["n"],
    #         cmap=opt["results"]["images"]["cmap"][i_p],
    #         unit=opt["results"]["images"]["units"][i_p]
    #     )

    #     maps.plot_maps_ensemble(
    #         ddpm_ensemble,
    #         output_dir_ddpm,
    #         param=p,
    #         n_members=ens_opt_ddpm["n_members"],
    #         n=opt["results"]["images"]["n"],
    #         cmap=opt["results"]["images"]["cmap"][i_p],
    #         unit=opt["results"]["images"]["units"][i_p]
    #     )

    #     # plot stats
    #     mean_arome = stats.compute_pointwise_mean(arome_ensemble, ens_opt_arome["n_members"], opt["data_loading"]["params_out"])
    #     std_arome  = stats.compute_pointwise_std(arome_ensemble, ens_opt_arome["n_members"], opt["data_loading"]["params_out"])
    #     Q5_arome   = stats.compute_pointwise_Q5(arome_ensemble, ens_opt_arome["n_members"], opt["data_loading"]["params_out"])
    #     Q95_arome  = stats.compute_pointwise_Q95(arome_ensemble, ens_opt_arome["n_members"], opt["data_loading"]["params_out"])
    #     mean_ddpm  = stats.compute_pointwise_mean(ddpm_ensemble , ens_opt_ddpm["n_members"] , opt["data_loading"]["params_out"])
    #     std_ddpm   = stats.compute_pointwise_std(ddpm_ensemble , ens_opt_ddpm["n_members"] , opt["data_loading"]["params_out"])
    #     Q5_ddpm    = stats.compute_pointwise_Q5(ddpm_ensemble , ens_opt_ddpm["n_members"] , opt["data_loading"]["params_out"])
    #     Q95_ddpm   = stats.compute_pointwise_Q95(ddpm_ensemble , ens_opt_ddpm["n_members"] , opt["data_loading"]["params_out"])

    #     mean = lde.group_ensembles(mean_arome, mean_ddpm) 
    #     std  = lde.group_ensembles(std_arome, std_ddpm) 
    #     Q95  = lde.group_ensembles(Q5_arome, Q5_ddpm)
    #     Q5   = lde.group_ensembles(Q95_arome, Q95_ddpm)

    #     print("plotting stats ...")
    
    #     stats.synthesis_unique_all_stats_ensemble(
    #         mean,
    #         std,
    #         Q5,
    #         Q95,
    #         output_dir,
    #         p
    #     )

    #     stats.synthesis_stat_distrib(
    #         mean,
    #         std,
    #         Q5,
    #         Q95,
    #         output_dir,
    #         p
    #     )


    # wind modulus
    # The next part was made to compute the modulus of the wind given its components, 
    # because the modulus was not available as an input parameter. It is not the case anymore
    if opt["ensemble"]["modulus"]:
        print("computing modulus ...")
        modulus_arome = pd.DataFrame(
            [],
            columns = ["dates", "echeances"] + ["modulus_" + str(j+1) for j in range(ens_opt_arome["n_members"])]
        )

        modulus_ddpm = pd.DataFrame(
            [],
            columns = ["dates", "echeances"]  + ["modulus_" + str(j+1) for j in range(ens_opt_ddpm["n_members"])]
        )


        for i in range(len(arome_ensemble)):

            values_arome = []
            for j in range(ens_opt_arome["n_members"]):
                mod_arome = np.sqrt(arome_ensemble["u10_" + str(j+1)].iloc[i]**2 + arome_ensemble["v10_" + str(j+1)].iloc[i]**2)
                values_arome.append(mod_arome)

            modulus_arome.loc[len(modulus_arome)] = [arome_ensemble.dates.iloc[i], arome_ensemble.echeances.iloc[i]] + \
                values_arome

            values_ddpm = []
            for j in range(ens_opt_ddpm["n_members"]):
                mod_ddpm  = np.sqrt(ddpm_ensemble["u10_" + str(j+1)].iloc[i]**2 + ddpm_ensemble["v10_" + str(j+1)].iloc[i]**2)
                values_ddpm.append(mod_ddpm)

            modulus_ddpm.loc[len(modulus_ddpm)] = [ddpm_ensemble.dates.iloc[i], ddpm_ensemble.echeances.iloc[i]] + \
                values_ddpm
            
        modulus_arome = lde.add_input_output(
            modulus_arome,
            opt["data_loading"]["interp"],
            opt["data_loading"]["data_test_location"],
            ["modulus"]
        )

        modulus_ddpm = lde.add_input_output(
            modulus_ddpm,
            opt["data_loading"]["interp"],
            opt["data_loading"]["data_test_location"],
            ["modulus"]
        )

        output_dir = os.path.join(opt["path"]["working_dir"], "modulus/")
        os.makedirs(output_dir, exist_ok=True)
        output_dir_arome = os.path.join(output_dir, "arome/")
        os.makedirs(output_dir_arome, exist_ok=True)
        output_dir_ddpm = os.path.join(output_dir, "ddpm/")
        os.makedirs(output_dir_ddpm, exist_ok=True)

        # plot maps
        print("Plotting modulus maps ...")
        maps.plot_maps_ensemble(
            modulus_arome,
            output_dir_arome,
            param="modulus",
            n_members=ens_opt_arome["n_members"],
            n=opt["results"]["images"]["n"],
            cmap="viridis",
            unit="m/s"
        )

        maps.plot_maps_ensemble(
            modulus_ddpm,
            output_dir_ddpm,
            param="modulus",
            n_members=ens_opt_ddpm["n_members"],
            n=opt["results"]["images"]["n"],
            cmap="viridis",
            unit="m/s"
        )

        # plot stats
        mean_arome = stats.compute_pointwise_mean(modulus_arome, ens_opt_arome["n_members"], ["modulus"])
        std_arome  = stats.compute_pointwise_std(modulus_arome, ens_opt_arome["n_members"], ["modulus"])
        Q5_arome   = stats.compute_pointwise_Q5(modulus_arome, ens_opt_arome["n_members"], ["modulus"])
        Q95_arome  = stats.compute_pointwise_Q95(modulus_arome, ens_opt_arome["n_members"], ["modulus"])
        mean_ddpm  = stats.compute_pointwise_mean(modulus_ddpm , ens_opt_ddpm["n_members"] , ["modulus"])
        std_ddpm   = stats.compute_pointwise_std(modulus_ddpm , ens_opt_ddpm["n_members"] , ["modulus"])
        Q5_ddpm    = stats.compute_pointwise_Q5(modulus_ddpm , ens_opt_ddpm["n_members"] , ["modulus"])
        Q95_ddpm   = stats.compute_pointwise_Q95(modulus_ddpm , ens_opt_ddpm["n_members"] , ["modulus"])

        mean = lde.group_ensembles(mean_arome, mean_ddpm) 
        std  = lde.group_ensembles(std_arome, std_ddpm) 
        Q5   = lde.group_ensembles(Q5_arome, Q5_ddpm)
        Q95  = lde.group_ensembles(Q95_arome, Q95_ddpm)

        print("plotting modulus stats ...")
        stats.synthesis_all_stats_ensemble(
            mean,
            std,
            Q5,
            Q95,
            output_dir,
            "modulus",
            n=opt["results"]["images"]["n"]
        )

        stats.synthesis_stat_distrib(
            mean,
            std,
            Q5,
            Q95,
            output_dir,
            "modulus"
        )

        stats.plot_std_echeance(std, output_dir, "modulus")
