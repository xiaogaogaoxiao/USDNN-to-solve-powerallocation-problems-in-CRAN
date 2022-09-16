

#from packages import *
#from parameters import *
from functions import *
import tensorflow as tf



def loss_DF_WN(Lambda=10**0.5, v_tau=0.25):
  def DF_loss(G, y_out):
    ''' compute loss without normalization (principale loss used in the paper)'''
    Tau = tf.constant(v_tau, dtype=tf.float32) # ==> Tau 
    
    W = tf.constant(Lambda, dtype=tf.float32)  # ==> lambda 
    
    G = tf.cast(G, dtype='float32')
    y_out = tf.cast(y_out, dtype='float32')
    
    # index retrieval

    Grp_indx, Gpp_indx, Gsr_indx, Gpr_indx, Gss_indx, Grs_indx, Gsp_indx, Gps_indx  = [0], [1], [2], [3], [4], [5], [6], [7]
    Alpha_indx, Pr_indx, Ps_indx  = [0], [1], [2]

    # tensors retrieval
    Grp, Gpp, Gsr, Gpr, Gss, Grs, Gsp, Gps, Alpha, Pr, Ps = tf.gather(G, Grp_indx, axis=1), tf.gather(G, Gpp_indx, axis=1), tf.gather(G, Gsr_indx, axis=1), tf.gather(G, Gpr_indx, axis=1), tf.gather(G, Gss_indx, axis=1), tf.gather(G, Grs_indx, axis=1), tf.gather(G, Gsp_indx, axis=1), tf.gather(G, Gps_indx, axis=1), tf.gather(y_out, Alpha_indx, axis=1), tf.gather(y_out, Pr_indx, axis=1), tf.gather(y_out, Ps_indx, axis=1)

    #  Primary power Creation
    
    Pp = tf.multiply(tf.ones(tf.shape(Pr), dtype=tf.dtypes.float32),10)
    
    # SNR1 : (Gsr*(1-alpha**2)*Ps**2)/(Gpr*Pp+1)
    SNR1 = tf.multiply(Gsr,(tf.multiply(tf.subtract(tf.constant(1,dtype=tf.float32), tf.pow(Alpha, 2)), tf.pow(Ps, 2))))
    SNR1 = tf.divide(SNR1, tf.add(tf.multiply(Gpr, Pp), tf.constant(1,dtype=tf.float32)))

    # SNR2 : ((Gss*Ps**2+Grs*Pr**2)+2*(np.sqrt(Grs*Gss)*Alpha*Ps*Pr)) ==> L1+L2/Gps*Pp+1
    L1 = tf.add(tf.multiply(Gss,tf.pow(Ps,2)),tf.multiply(Grs,tf.pow(Pr,2)))
    L2 = tf.multiply(tf.constant(2,dtype=tf.float32),tf.multiply(tf.multiply(tf.sqrt(tf.multiply(Grs,Gss)),Ps),tf.multiply(Alpha,Pr)))
    
    SNR2 = tf.add(L1,L2)
    SNR2= tf.divide(SNR2, tf.add(tf.multiply(Gps, Pp),tf.constant(1,dtype=tf.float32)))
    
    SNR_opt = tf.minimum(SNR1, SNR2)

    ########### QoS ################
    
    # function A' ==> A'(Gpp) : ((Gpp*Pp)/((1+(Gpp*Pp))**(1-tau)-1))-1 ==> (Gpp*Pp)/(R1) 
    R1 = tf.add(tf.constant(1, dtype=tf.float32),tf.multiply(Gpp,Pp))
    R1 = tf.pow(R1, tf.math.subtract(tf.constant(1, dtype=tf.float32),Tau))
    R1 = tf.math.subtract(R1,tf.constant(1, dtype=tf.float32))

    A_ = tf.subtract(tf.divide(tf.multiply(Gpp,Pp),R1),tf.constant(1, dtype=tf.float32))
  

    #Qos = (Gsp*Ps**2+Grp*Pr**2+2*np.sqrt(Gsp*Grp)*Alpha*Ps*Pr)-A_
    Qos = tf.add(tf.add(tf.multiply(Gsp,tf.pow(Ps,2)),tf.multiply(Grp,tf.pow(Pr,2))),tf.multiply(tf.constant(2,dtype=tf.float32),tf.multiply(tf.sqrt(tf.multiply(Gsp,Grp)),tf.multiply(Ps,tf.multiply(Alpha,Pr)))))
    
    Qos = tf.subtract(Qos, A_)

    n_Qos = tf.multiply(W,tf.keras.activations.relu(Qos)) 
    
    Rs_opt =  tf.multiply(tf.constant(0.5, dtype=tf.float32),log2(tf.add(tf.constant(1,dtype=tf.float32),SNR_opt)))

    #-n_SNR+n_Qos
    res = tf.reduce_mean(-Rs_opt+n_Qos) 

    return res
  return DF_loss

def loss_DF(Lambda, v_tau):
  def DF_loss(G, y_out):
    ''' compute loss with normalization'''

    Tau = tf.constant(v_tau, dtype=tf.float32) # ==> Tau 
    W = tf.constant(Lambda, dtype=tf.float32)  # ==> lambda 
    
    G = tf.cast(G, dtype='float32')
    y_out = tf.cast(y_out, dtype='float32')
    
    # index retrieval

    Grp_indx, Gpp_indx, Gsr_indx, Gpr_indx, Gss_indx, Grs_indx, Gsp_indx, Gps_indx, Alpha_hat_indx, Pr_hat_indx, Ps_hat_indx   = [0], [1], [2], [3], [4], [5], [6], [7], [8], [9], [10]
    Alpha_indx, Pr_indx, Ps_indx  = [0], [1], [2]

    # tensors retrieval
    Grp, Gpp, Gsr, Gpr, Gss, Grs, Gsp, Gps, Alpha_hat, Pr_hat, Ps_hat, Alpha, Pr, Ps = tf.gather(G, Grp_indx, axis=1), tf.gather(G, Gpp_indx, axis=1), tf.gather(G, Gsr_indx, axis=1), tf.gather(G, Gpr_indx, axis=1), tf.gather(G, Gss_indx, axis=1), tf.gather(G, Grs_indx, axis=1), tf.gather(G, Gsp_indx, axis=1) , tf.gather(G, Gps_indx, axis=1), tf.gather(G, Alpha_hat_indx, axis=1), tf.gather(G, Pr_hat_indx, axis=1), tf.gather(G, Ps_hat_indx, axis=1), tf.gather(y_out, Alpha_indx, axis=1), tf.gather(y_out, Pr_indx, axis=1), tf.gather(y_out, Ps_indx, axis=1)

    #  Primary power Creation
    
    Pp = tf.multiply(tf.ones(tf.shape(Pr), dtype=tf.dtypes.float32),10)
    
    # SNR1 : (Gsr*(1-alpha**2)*Ps**2)/(Gpr*Pp+1)
    SNR1 = tf.multiply(Gsr,(tf.multiply(tf.subtract(tf.constant(1,dtype=tf.float32), tf.pow(Alpha, 2)), tf.pow(Ps, 2))))
    SNR1 = tf.divide(SNR1, tf.add(tf.multiply(Gpr, Pp), tf.constant(1,dtype=tf.float32)))

    # SNR2 : ((Gss*Ps**2+Grs*Pr**2)+2*(np.sqrt(Grs*Gss)*Alpha*Ps*Pr))/(Gps*Pp+1) ==> L1+L2/ (Gps*Pp+1)
    L1 = tf.add(tf.multiply(Gss,tf.pow(Ps,2)),tf.multiply(Grs,tf.pow(Pr,2)))
    L2 = tf.multiply(tf.constant(2,dtype=tf.float32),tf.multiply(tf.multiply(tf.sqrt(tf.multiply(Grs,Gss)),Ps),tf.multiply(Alpha,Pr)))
    
    SNR2 = tf.add(L1,L2)
    SNR2 = tf.divide(SNR2, tf.add(tf.multiply(Gps, Pp),tf.constant(1,dtype=tf.float32)))
    
    SNR_opt = tf.minimum(SNR1, SNR2)

    ########### QoS ################
    
    # function A' ==> A'(Gpp) : ((Gpp*Pp)/((1+(Gpp*Pp))**(1-tau)-1))-1 ==> (Gpp*Pp)/(R1) 
    R1 = tf.add(tf.constant(1, dtype=tf.float32),tf.multiply(Gpp,Pp))
    R1 = tf.pow(R1, tf.math.subtract(tf.constant(1, dtype=tf.float32),Tau))
    R1 = tf.math.subtract(R1,tf.constant(1, dtype=tf.float32))

    A_ = tf.subtract(tf.divide(tf.multiply(Gpp,Pp),R1),tf.constant(1, dtype=tf.float32))

    #Qos = (Gsp*Ps**2+Grp*Pr**2+2*np.sqrt(Gsp*Grp)*Alpha*Ps*Pr)-A_/A_
    
    Qos = tf.add(tf.add(tf.multiply(Gsp,tf.pow(Ps,2)),tf.multiply(Grp,tf.pow(Pr,2))),tf.multiply(tf.constant(2,dtype=tf.float32),tf.multiply(tf.sqrt(tf.multiply(Gsp,Grp)),tf.multiply(Ps,tf.multiply(Alpha,Pr)))))
    Qos = tf.subtract(Qos, A_)
    
    ################################
    # SNR max :
    # SNR1_max : (Gsr*(1-Alpha_hat**2)*Ps_hat**2)/(Gpr*Pp+1)
    SNR1_max = tf.multiply(Gsr,(tf.multiply(tf.subtract(tf.constant(1,dtype=tf.float32), tf.pow(Alpha_hat,2)), tf.pow(Ps_hat,2))))
    SNR1_max = tf.divide(SNR1_max, tf.add(tf.multiply(Gpr, Pp), tf.constant(1,dtype=tf.float32)))
    
    # SNR2_max : ((Gss*Ps_hat,2**2+Grs*Pr_hat**2)+2*(np.sqrt(Grs*Gss)*Alpha_hat*Ps_hat*Pr_hat))/(Gps*Pp+1) ==> L1+L2/ (Gps*Pp+1)

    L1 = tf.add(tf.multiply(Gss,tf.pow(Ps_hat,2)),tf.multiply(Grs,tf.pow(Pr_hat,2)))
    L2 = tf.multiply(tf.constant(2,dtype=tf.float32),tf.multiply(tf.multiply(tf.sqrt(tf.multiply(Grs,Gss)),Ps_hat),tf.multiply(Alpha_hat,Pr_hat)))
    
    SNR2_max = tf.add(L1,L2)
    SNR2_max = tf.divide(SNR2_max, tf.add(tf.multiply(Gps, Pp),tf.constant(1,dtype=tf.float32)))

    SNR_max = tf.minimum(SNR1_max, SNR2_max)

    # Normalization
    n_Qos = tf.divide(Qos, A_)
    n_SNR = tf.divide(SNR_opt, SNR_max)

    n_Qos = tf.multiply(W,tf.keras.activations.relu(n_Qos)) 
    #-n_SNR+n_Qos
    res = tf.reduce_mean(-n_SNR+n_Qos) 

    return res
  return DF_loss


