import numpy as np
import matplotlib.pyplot as plt
from numba import njit

# --------------------
# Metropolis Algorithm
# --------------------

def ini_config(N, model_type):

    # random initial configuration
    # check what type of model
    if model_type == 0:
        config = np.random.choice([-1, 1],(N+2, N+2))
    elif model_type == 1:
        config = np.random.uniform(0,1,(N+2, N+2))

    # temp holds all initial config data
    temp_config = config[1:N+1,1:N+1].copy()

    # -------------------
    # Ghost Cells
    # -------------------
    # the ghost cell are changed to match periodic bcs and wraps around lattice
    for x in range(N):
        config[0,x+1] = temp_config[-1,x]
        config[-1,x+1] = temp_config[0,x]
        config[x+1,0] = temp_config[x,-1]
        config[x+1,-1] = temp_config[x,0]

    return config

@njit
def periodic_bcs(config, I, J, N):

    # if chosen grid point is adjacent to ghostcell adjust bcs wrap accordingly

    # adjacent row
    if I == 1:
        config[-1,J] = config[I,J]
    elif I == N+1:
        config[0,J] = config[I,J]

    # adjacent column
    if J == 1:
        config[I,-1] = config[I,J]
    elif J == N+1:
        config[I,0] = config[I,J]

    return config

@njit
def reject_samp(config, mag_field, interaction, beta, N, model_type):
    
    # --------------------
    # Random Flip Change
    # --------------------
    # randomly choose a grid point (I,J) in lattice to flip/change spin
    I = np.random.randint(1, N+2)
    J = np.random.randint(1, N+2)
    old_spin = config[I,J]

    # neighbours of the chosen point
    neighbours = np.array([config[I+1,J], config[I-1,J], config[I,J+1], config[I,J-1]])
    
    # calculate energy difference before and after flip/change
    if model_type == 0:
        energy_0 = old_spin * mag_field - interaction * sum(old_spin * neighbours)
        new_spin = -1 * old_spin
        energy_t = new_spin * mag_field - interaction * sum(new_spin * neighbours)
        delta_energy = energy_t - energy_0
    elif model_type == 1:
        energy_0 = mag_field * np.cos(old_spin) - interaction * sum(np.cos( 2 * np.pi * (old_spin - neighbours)))
        new_spin = np.random.uniform(0,1)
        energy_t = mag_field * np.cos(new_spin) - interaction * sum(np.cos( 2 * np.pi * (new_spin - neighbours)))
        delta_energy = energy_t - energy_0

    # calculate transition probability
    ratio = np.exp(-beta * delta_energy)
    randnum = np.random.random()

    # --------------------
    # Rejection Sample
    # --------------------
    # accept new configuration if certain conditions are met:

    # accept if new energy is lower (energy efficient)
    if delta_energy <= 0:
        config[I,J] = new_spin
        config = periodic_bcs(config, I, J, N)
    # accept with random transition probability
    elif ratio >= randnum:
        config[I,J] = new_spin
        config = periodic_bcs(config, I, J, N)
    # in the event of rejection, return old lattice

    return config

@njit
def sweep(config, mag_field, interaction, beta, N, model_type):

    # ----------
    # One Sweep
    # ----------
    # after one sweep, each grid point has been flipped and accepted/rejected once
    for i in range(N*N):
        config = reject_samp(config, mag_field, interaction, beta, N, model_type)

    return config
