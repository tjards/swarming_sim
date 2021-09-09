#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Compute the control inputs for dynamic encirclement tactic  

Created on Mon Jan  4 12:45:55 2021

@author: tjards

"""

import numpy as np
import reynolds_tools 

#%% Setup hyperparameters

# === Saber Flocking =====
a = 0.5
b = 0.5
c = np.divide(np.abs(a-b),np.sqrt(4*a*b)) 
eps = 0.1
#eps = 0.5
h = 0.9
pi = 3.141592653589793

# gains
c1_a = 2                # lattice flocking
c2_a = 2*np.sqrt(2)
c1_b = 1                # obstacle avoidance
c2_b = 2*np.sqrt(1)
c1_g = 3                # target tracking
c2_g = 2*np.sqrt(3)

# === Encirclement+ ===
c1_d = 2                # encirclement 
c2_d = 2*np.sqrt(2)

# === Reynolds Flocking ===
cd_1 = 0.4              # cohesion
cd_2 = 0.3              # alignment
cd_3 = 0.8              # separation
cd_4 = 0                # navigation (default 0)
maxu = 10               # max input (per rule)
maxv = 100              # max v
far_away = 500          # when to go back to centroid
agents_min_coh = 5      # min number of agents
mode_min_coh = 0        # enforce min # of agents (0 = no, 1 = yes)
cd_escort = 0.5         # gain to use for escort


#%% Some function that are used often
# ---------------------------------

def regnorm(z):
    norm = np.divide(z,np.linalg.norm(z))
    return norm

def sigma_norm(z):    
    norm_sig = (1/eps)*(np.sqrt(1+eps*np.linalg.norm(z)**2)-1)
    return norm_sig
    
def n_ij(q_i, q_j):
    n_ij = np.divide(q_j-q_i,np.sqrt(1+eps*np.linalg.norm(q_j-q_i)**2))    
    return n_ij

def sigma_1(z):    
    sigma_1 = np.divide(z,np.sqrt(1+z**2))    
    return sigma_1

def rho_h(z):    
    if 0 <= z < h:
        rho_h = 1        
    elif h <= z < 1:
        rho_h = 0.5*(1+np.cos(pi*np.divide(z-h,1-h)))    
    else:
        rho_h = 0  
    return rho_h
 
def phi_a(q_i, q_j, r_a, d_a): 
    z = sigma_norm(q_j-q_i)        
    phi_a = rho_h(z/r_a) * phi(z-d_a)    
    return phi_a
    
def phi(z):    
    phi = 0.5*((a+b)*sigma_1(z+c)+(a-b))    
    return phi 
        
def a_ij(q_i, q_j, r_a):        
    a_ij = rho_h(sigma_norm(q_j-q_i)/r_a)
    return a_ij

def b_ik(q_i, q_ik, d_b):        
    b_ik = rho_h(sigma_norm(q_ik-q_i)/d_b)
    return b_ik

def phi_b(q_i, q_ik, d_b): 
    z = sigma_norm(q_ik-q_i)        
    phi_b = rho_h(z/d_b) * (sigma_1(z-d_b)-1)    
    return phi_b

# Reynolds flocking functions 
def norm_sat(u,maxu):
    norm1b = np.linalg.norm(u)
    u_out = maxu*np.divide(u,norm1b)
    return u_out


    
#%% Tactic Command Equations 
# ------------------------
def commands(states_q, states_p, obstacles, walls, r, d, r_prime, d_prime, targets, targets_v, targets_enc, targets_v_enc, swarm_prox, tactic_type, centroid, escort):   
    
    # initialize 
    r_a = sigma_norm(r)                         # lattice separation (sensor range)
    d_a = sigma_norm(d)                         # lattice separation (goal)
    r_b = sigma_norm(r_prime)                   # obstacle separation (sensor range)
    d_b = sigma_norm(d_prime)                   # obstacle separation (goal range)
    u_int = np.zeros((3,states_q.shape[1]))     # interactions
    u_obs = np.zeros((3,states_q.shape[1]))     # obstacles 
    u_nav = np.zeros((3,states_q.shape[1]))     # navigation
    u_enc = np.zeros((3,states_q.shape[1]))     # encirclement 
    #u_enc2 = np.zeros((3,states_q.shape[1]))    # ensherement
    cmd_i = np.zeros((3,states_q.shape[1]))     # store the commands
    
    u_coh = np.zeros((3,states_q.shape[1]))  # cohesion
    u_ali = np.zeros((3,states_q.shape[1]))  # alignment
    u_sep = np.zeros((3,states_q.shape[1]))  # separation
    distances = np.zeros((states_q.shape[1],states_q.shape[1])) # to store distances between nodes
    
    
    # to find the radius that includes min number of agents
    if mode_min_coh == 1:
        slide = 0
        for k_node in range(states_q.shape[1]):
            #slide += 1
            for k_neigh in range(slide,states_q.shape[1]):
                if k_node != k_neigh:
                    distances[k_node,k_neigh] = np.linalg.norm(states_q[:,k_node]-states_q[:,k_neigh])
        
    # # initialize 
    # r_b = sigma_norm(r_prime)                   # obstacle separation (sensor range)
    # d_b = sigma_norm(d_prime)                   # obstacle separation (goal range)
    # u_obs = np.zeros((3,states_q.shape[1]))     # obstacles 
    # u_enc = np.zeros((3,states_q.shape[1]))     # encirclement 
    # cmd_i = np.zeros((3,states_q.shape[1]))     # store the commands
    
    # for each vehicle/node in the network
    for k_node in range(states_q.shape[1]): 
         
        # if reynolds flocking 
        if tactic_type == 0:
            
            # Reynolds Flocking
            # ------------------  
            
            #initialize for this node
            temp_total = 0
            temp_total_prime = 0
            temp_total_coh = 0
            sum_poses = np.zeros((3))
            sum_velos = np.zeros((3))
            sum_obs = np.zeros((3))
            u_coh = np.zeros((3,states_q.shape[1]))  # cohesion
            u_ali = np.zeros((3,states_q.shape[1]))  # alignment
            u_sep = np.zeros((3,states_q.shape[1]))  # separation
            
            # adjust cohesion range for min number of agents 
            if mode_min_coh == 1:
                r_coh = 0
                #agents_min_coh = 5
                node_ranges = distances[k_node,:]
                node_ranges_sorted = np.sort(node_ranges)
                r_coh_temp = node_ranges_sorted[agents_min_coh+1]
                r_coh = r_coh_temp
                #print(r_coh)
            else:
                r_coh = r

   
            # search through each neighbour
            for k_neigh in range(states_q.shape[1]):
                # except for itself (duh):
                if k_node != k_neigh:
                    # compute the euc distance between them
                    dist = np.linalg.norm(states_q[:,k_node]-states_q[:,k_neigh])
                    
                    if dist < 0.1:
                        print('collision at agent: ', k_node)
                        continue

                    # if it is within the alignment range
                    if dist < np.maximum(r,r_coh):
 
                        # count
                        temp_total += 1                        
             
                        # sum 
                        #sum_poses += states_q[:,k_neigh]
                        sum_velos += states_p[:,k_neigh]

                    # if within cohesion range 
                    if dist < np.maximum(r,r_coh):
                        
                        #count
                        temp_total_coh += 1
                        
                        #sum
                        sum_poses += states_q[:,k_neigh]


                    # if within the separation range 
                    if dist < r_prime:
                        
                        # count
                        temp_total_prime += 1
                        
                        # sum of obstacles 
                        sum_obs += -(states_q[:,k_node]-states_q[:,k_neigh])/(dist**2)                        

            # norms
            # -----
            norm_coh = np.linalg.norm(sum_poses)
            norm_ali = np.linalg.norm(sum_velos)
            norm_sep = np.linalg.norm(sum_obs)
  
            if temp_total != 0:
                
                # Cohesion
                # --------
                if norm_coh != 0:
                    #temp_u_coh = (maxv*np.divide(((np.divide(sum_poses,temp_total) - states_q[:,k_node])),norm_coh)-states_p[:,k_node])
                    temp_u_coh = (maxv*np.divide(((np.divide(sum_poses,temp_total_coh) - states_q[:,k_node])),norm_coh)-states_p[:,k_node])
                    u_coh[:,k_node] = cd_1*norm_sat(temp_u_coh,maxu)
                    #print(temp_total_coh)
                
                # Alignment
                # ---------
                if norm_ali != 0:                 
                    temp_u_ali = (maxv*np.divide((np.divide(sum_velos,temp_total)),norm_ali)-states_p[:,k_node])
                    u_ali[:,k_node] = cd_2*norm_sat(temp_u_ali,maxu)

            if temp_total_prime != 0 and norm_sep != 0:
                    
                # Separtion
                # ---------
                temp_u_sep = (maxv*np.divide(((np.divide(sum_obs,temp_total_prime))),norm_sep)-states_p[:,k_node]) 
                u_sep[:,k_node] = -cd_3*norm_sat(temp_u_sep,maxu)
                        
            # Tracking
            # --------           
            
            # if far away
            if np.linalg.norm(centroid.transpose()-states_q[:,k_node]) > far_away:
                cd_4 = 0.05
            else:
                cd_4 = 0

            if escort == 1:
                cd_4 = cd_escort
                temp_u_nav = (targets[:,k_node]-states_q[:,k_node])
            else:
                temp_u_nav = (centroid.transpose()-states_q[:,k_node])
            u_nav[:,k_node] = cd_4*norm_sat(temp_u_nav,maxu)
            

        # if flocking                                 
        if tactic_type == 1:
        
            # Lattice Flocking term (phi_alpha)
            # --------------------------------            
            # search through each neighbour
            for k_neigh in range(states_q.shape[1]):
                # except for itself (duh):
                if k_node != k_neigh:
                    # compute the euc distance between them
                    dist = np.linalg.norm(states_q[:,k_node]-states_q[:,k_neigh])
                    # if it is within the interaction range
                    if dist < r:
                        # compute the interaction command
                        u_int[:,k_node] += c1_a*phi_a(states_q[:,k_node],states_q[:,k_neigh],r_a, d_a)*n_ij(states_q[:,k_node],states_q[:,k_neigh]) + c2_a*a_ij(states_q[:,k_node],states_q[:,k_neigh],r_a)*(states_p[:,k_neigh]-states_p[:,k_node]) 
          
            # Navigation term (phi_gamma)
            # ---------------------------
            u_nav[:,k_node] = - c1_g*sigma_1(states_q[:,k_node]-targets[:,k_node])-c2_g*(states_p[:,k_node] - targets_v[:,k_node])
      
              
        # Obstacle Avoidance term (phi_beta)
        # ---------------------------------   
        # search through each obstacle 
        for k_obstacle in range(obstacles.shape[1]):

            # compute norm between this node and this obstacle
            normo = np.linalg.norm(states_q[:,k_node]-obstacles[0:3,k_obstacle])
            
            # ignore if overlapping
            #if normo == 0:
            if normo < 0.2:
                continue 
            
            # compute mu
            mu = np.divide(obstacles[3, k_obstacle],normo)
            # compute bold_a_k (for the projection matrix)
            bold_a_k = np.divide(states_q[:,k_node]-obstacles[0:3,k_obstacle],normo)
            bold_a_k = np.array(bold_a_k, ndmin = 2)
            # compute projection matrix
            P = np.identity(states_p.shape[0]) - np.dot(bold_a_k,bold_a_k.transpose())
            # compute beta-agent position and velocity
            q_ik = mu*states_q[:,k_node]+(1-mu)*obstacles[0:3,k_obstacle]
            # compute distance to beta-agent
            dist_b = np.linalg.norm(q_ik-states_q[:,k_node])
            # if it is with the beta range
            if dist_b < r_prime:
                # compute the beta command
                p_ik = mu*np.dot(P,states_p[:,k_node])    
                u_obs[:,k_node] += c1_b*phi_b(states_q[:,k_node], q_ik, d_b)*n_ij(states_q[:,k_node], q_ik) + c2_b*b_ik(states_q[:,k_node], q_ik, d_b)*(p_ik - states_p[:,k_node])
               
        # search through each wall (a planar obstacle)
        for k_wall in range(walls.shape[1]):
            
            # define the wall
            bold_a_k = np.array(np.divide(walls[0:3,k_wall],np.linalg.norm(walls[0:3,k_wall])), ndmin=2).transpose()    # normal vector
            y_k = walls[3:6,k_wall]         # point on plane
            # compute the projection matrix
            P = np.identity(y_k.shape[0]) - np.dot(bold_a_k,bold_a_k.transpose())
            # compute the beta_agent 
            q_ik = np.dot(P,states_q[:,k_node]) + np.dot((np.identity(y_k.shape[0])-P),y_k)
            # compute distance to beta-agent
            dist_b = np.linalg.norm(q_ik-states_q[:,k_node])
            # if it is with the beta range
            maxAlt = 10 # TRAVIS: maxAlt is for testing, only enforces walls below this altitude
            if dist_b < r_prime and states_q[2,k_node] < maxAlt:
                p_ik = np.dot(P,states_p[:,k_node])
                u_obs[:,k_node] += c1_b*phi_b(states_q[:,k_node], q_ik, d_b)*n_ij(states_q[:,k_node], q_ik) + c2_b*b_ik(states_q[:,k_node], q_ik, d_b)*(p_ik - states_p[:,k_node])

        # if structured swarming
        if tactic_type == 2 or tactic_type == 8:    
            # Encirclement term (phi_delta)
            # ----------------------------    
            u_enc[:,k_node] = - c1_d*sigma_1(states_q[:,k_node]-targets_enc[:,k_node])-c2_d*(states_p[:,k_node] - targets_v_enc[:,k_node])    
        
        #safety (if venture too far, just navigate)
        # if prox_i > transition*10:
        #     cmd_i[:,k_node] = - c1_g*sigma_1(states_q[:,k_node]-targets[:,k_node])
        #     print('! Safety engaged on agent:',k_node)
        #     print('-- Agent prox: ',prox_i, 'f: ', f_i)
        #     print('-- Swarm prox: ', swarm_prox)
        #     continue
    
        # Conditional commands
        # ----------------------------------------------
        
        if tactic_type == 1:
            cmd_i[:,k_node] = u_int[:,k_node] + u_obs[:,k_node] + u_nav[:,k_node] 
        elif tactic_type == 0:
            cmd_i[:,k_node] = u_coh[:,k_node] + u_ali[:,k_node] + u_sep[:,k_node] + u_nav[:,k_node] 
        else:
            cmd_i[:,k_node] = u_obs[:,k_node] + u_enc[:,k_node] 

        #cmd_i[:,k_node] = reynolds_tools.compute_cmd(targets, centroid, states_q, states_p, k_node, r, r_prime, escort)
        #print('test')


    cmd = cmd_i    
    
    return cmd






#%% LEGACY 


                    # # if it is within the interaction range
                    # if dist < r:
                    #     # count
                    #     temp_total += 1                        
                                                
                    #     # cohesion                        
                    #     #u_dirty_1[:,k_node] += cd_1*sigma_norm(states_q[:,k_neigh]-states_q[:,k_node])
                        
                    #     #sum of positions
                        
                    #     sum_poses += states_q[:,k_neigh]
                    #     sum_velos += states_p[:,k_neigh]
                        
                    #     #sum_obs += states_q[:,k_neigh]/dist
                    #     sum_obs += -(states_q[:,k_node]-states_q[:,k_neigh])/(dist**2)
                        
                    #     # alignment
                    #     #u_dirty_2[:,k_node] += cd_2*sigma_norm(states_p[:,k_neigh]-states_p[:,k_node]) 
                    #     # separation
                    #     #u_dirty_3[:,k_node] += cd_3*sigma_norm(states_q[:,k_node]-states_q[:,k_neigh])


          # #u_dirty_1[:,k_node] = cd_1*((np.divide(sum_poses,np.maximum(temp_total,0.001)) - states_q[:,k_node]) -states_p[:,k_node])
          #   #u_dirty_1[:,k_node] = cd_1*(np.divide(sum_poses,np.maximum(temp_total,0.001)) - states_q[:,k_node])
          #   #u_dirty_1[:,k_node] = cd_1*sigma_1(np.divide(sum_poses,np.maximum(temp_total,0.001)) - states_q[:,k_node])
          #   #u_dirty_1[:,k_node] = cd_1*(np.divide(sum_poses,np.maximum(temp_total,0.001)) - states_q[:,k_node])
          #   #u_dirty_1[:,k_node] = cd_1*((np.divide(sum_poses,np.maximum(temp_total,0.001)) - states_q[:,k_node])-states_p[:,k_node])
          #   #u_dirty_1[:,k_node] = cd_1*((np.divide(sum_poses,np.maximum(temp_total,0.001)) - states_q[:,k_node]))/10 # works
            
          #   norm1 = np.linalg.norm(sum_poses)
          #   if norm1 != 0:
          #       if temp_total != 0:
                    
          #           # velocity to center of mass
          #           #com = np.divide(sum_poses,temp_total)
          #           #v_com = maxv*np.divide(com - states_q[:,k_node],norm1)
          #           #u_dirty_1[:,k_node] = cd_1*(v_com-states_p[:,k_node])/10
                    
          #           # new
          #           #u_dirty_1[:,k_node] = cd_1*((np.divide(sum_poses,temp_total) - states_q[:,k_node]))/10 
          #           #u_dirty_1[:,k_node] = cd_1*(maxv*np.divide(((np.divide(sum_poses,temp_total) - states_q[:,k_node])),norm1)-states_p[:,k_node]) # for sure worx
          #           #norm1b = np.linalg.norm(u_dirty_1[:,k_node])
          #           #u_dirty_1[:,k_node] = cd_1*(u_dirty_1[:,k_node])/norm1b
                    
          #           #u_dirty_1[:,k_node] = (maxv*np.divide(((np.divide(sum_poses,temp_total) - states_q[:,k_node])),norm1)-states_p[:,k_node]) # for sure worx
          #           #norm1b = np.linalg.norm(u_dirty_1[:,k_node])
          #           #u_dirty_1[:,k_node] = cd_1*maxu*np.divide(u_dirty_1[:,k_node],norm1b)
                    
          #           temp_u_coh = (maxv*np.divide(((np.divide(sum_poses,temp_total) - states_q[:,k_node])),norm1)-states_p[:,k_node])
          #           u_dirty_1[:,k_node] = cd_1*norm_sat(temp_u_coh,maxu)
                    

            # #u_dirty_2[:,k_node] = cd_2*(np.divide(sum_velos,np.maximum(temp_total,0.001)) - states_q[:,k_node])
            # #u_dirty_2[:,k_node] = cd_2*(np.divide(sum_velos,np.maximum(temp_total,0.001))) #- states_q[:,k_node])
            # #u_dirty_2[:,k_node] = cd_2*(np.divide(sum_velos,np.maximum(temp_total,0.001))) 
            # #u_dirty_2[:,k_node] = cd_2*(np.divide(sum_velos,np.maximum(temp_total,0.001)) - states_p[:,k_node])
            # #u_dirty_2[:,k_node] = cd_2*sigma_1(np.divide(sum_velos,np.maximum(temp_total,0.001)) - states_p[:,k_node])
            # #u_dirty_2[:,k_node] = cd_2*(np.divide(sum_velos,np.maximum(temp_total,0.001)) - states_p[:,k_node])
            
            # #u_dirty_2[:,k_node] = cd_2*(np.divide(sum_velos,np.maximum(temp_total,0.001)))/10  # works
            
            
            # norm2 = np.linalg.norm(sum_velos)
            # if norm2 != 0:
            #     if temp_total != 0:
                    
            #         #u_dirty_2[:,k_node] = cd_2*(maxv*np.divide((np.divide(sum_velos,temp_total)),norm2)-states_p[:,k_node])
            
            #         #new
            #         #u_dirty_2[:,k_node] = cd_2*(maxv*np.divide((np.divide(sum_velos,temp_total)),norm2)-states_p[:,k_node]) # for sure worx
            #         #norm2b = np.linalg.norm(u_dirty_2[:,k_node])
            #         #u_dirty_2[:,k_node] = cd_2*(u_dirty_2[:,k_node])/norm2b
            #         u_dirty_2[:,k_node] = (maxv*np.divide((np.divide(sum_velos,temp_total)),norm2)-states_p[:,k_node])
            #         norm2b = np.linalg.norm(u_dirty_2[:,k_node])
            #         u_dirty_2[:,k_node] = cd_2*maxu*np.divide(u_dirty_2[:,k_node],norm2b)
            
            
            #           # SEPARATION
            # # ----------
               
            # #u_dirty_3[:,k_node] = -cd_3*((np.divide(sum_obs,np.maximum(temp_total,0.001))) - states_p[:,k_node])
            # #u_dirty_3[:,k_node] = -cd_3*(np.divide(sum_obs,np.maximum(temp_total,0.001)))
            # #u_dirty_3[:,k_node] = -cd_3*sigma_1(np.divide(sum_obs,np.maximum(temp_total,0.001)))
            # #u_dirty_3[:,k_node] = -cd_3*(np.divide(sum_obs,np.maximum(temp_total,0.001)))
            # #u_dirty_3[:,k_node] = -cd_3*((np.divide(sum_obs,np.maximum(temp_total,0.001)))- states_p[:,k_node])
            # #u_dirty_3[:,k_node] = -cd_3*((np.divide(sum_obs,np.maximum(temp_total,0.001))))/10
           
            # norm3 = np.linalg.norm(sum_obs)
            
            # if dist < r_prime:
            #     if norm3 != 0:
            #         if temp_total != 0:
                        
            #             # velocity to center of mass
            #             #obs= np.divide(sum_obs,temp_total)
            #             #v_obs = maxv*np.divide(obs,norm3)
            #             #u_dirty_3[:,k_node] = cd_3*(v_obs-states_p[:,k_node])/10
                        
            #             #u_dirty_3[:,k_node] = -cd_3*((np.divide(sum_obs,temp_total)))/10
            #             #u_dirty_3[:,k_node] =cd_3*(maxv*np.divide(((np.divide(sum_obs,temp_total))),norm3)-states_p[:,k_node]) # for sure worx
            #             #norm3b = np.linalg.norm(u_dirty_3[:,k_node])
            #             #u_dirty_3[:,k_node] = cd_3*(u_dirty_3[:,k_node])/norm3b
            #             u_dirty_3[:,k_node] =(maxv*np.divide(((np.divide(sum_obs,temp_total))),norm3)-states_p[:,k_node]) 
            #             norm3b = np.linalg.norm(u_dirty_3[:,k_node])
            #             u_dirty_3[:,k_node] = -cd_3*maxu*np.divide(u_dirty_3[:,k_node],norm3b)
                  
            #             # COHESION
            # # -------
            
            # norm1 = np.linalg.norm(sum_poses)
            # if norm1 != 0:
            #     if temp_total != 0:
                    
            #         temp_u_coh = (maxv*np.divide(((np.divide(sum_poses,temp_total) - states_q[:,k_node])),norm1)-states_p[:,k_node])
            #         u_dirty_1[:,k_node] = cd_1*norm_sat(temp_u_coh,maxu)
                    

            # # ALIGNMENT
            # # --------
            
            # norm2 = np.linalg.norm(sum_velos)
            # if norm2 != 0:
            #     if temp_total != 0:
                    
            #         temp_u_ali = (maxv*np.divide((np.divide(sum_velos,temp_total)),norm2)-states_p[:,k_node])
            #         u_dirty_2[:,k_node] = cd_2*norm_sat(temp_u_ali,maxu)

 
            # # SEPARATION
            # # ----------
               
            # norm3 = np.linalg.norm(sum_obs)
            
            # if dist < r_prime:
            #     if norm3 != 0:
            #         if temp_total != 0:
                                               
            #             temp_u_sep = (maxv*np.divide(((np.divide(sum_obs,temp_total))),norm3)-states_p[:,k_node]) 
            #             u_dirty_3[:,k_node] = -cd_3*norm_sat(temp_u_sep,maxu)