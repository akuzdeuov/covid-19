import numpy as np 
import matplotlib.pyplot as plt 


class Node:
    def __init__(self):
        self.param_br = 0.02 / 365    # Daily birth rate
        self.param_dr = 0.01 / 365    # Daily mortality rate except infected people
        self.param_vr = 0.02          # Daily vaccination rate (Ratio of susceptible 
                                       # population getting vaccinated)
        self.param_vir = 0.9          # Ratio of the immunized after vaccination
        self.param_mir = 0.0          # Maternal immunization rate
        self.param_beta_exp = 0.5     # Susceptible to exposed transition constant
        self.param_qr  = 0.1          # Daily quarantine rate (Ratio of Exposed getting Quarantined)
        self.param_beta_inf = 0.0     # Susceptible to infected transition constant
        self.param_ir  = 0.1          # Daily isolation rate (Ratio of Infected getting Isolated)
        
        self.param_eps_exp = 0.7      # Disease transmission rate of exposed compared to the infected
        self.param_eps_qua = 0.3      # Disease transmission rate of quarantined compared to the infected
        self.param_eps_iso = 0.3      # Disease transmission rate of isolated compared to the
        
        self.param_gamma_mor = 0.4    # Infected to Dead transition probability
        self.param_gamma_im = 0.0     # Infected to Recovery Immunized transition probability
        
        self.param_dt = 1/24          # Sampling time in days (1/24 corresponds to one hour)
        self.param_sim_len = 100      # Length of simulation in days
        self.param_num_states = 0     # Number of states
        self.param_num_sim = int(self.param_sim_len / self.param_dt) + 1       # Number of simulation
        
        self.param_t_exp = 3          # Incubation period (The period from the start of 
                                      # incubation to the end of the incubation state)
        self.param_t_inf = 5          # Infection period (The period from the start of 
                                      # infection to the end of the infection state)
        self.param_t_vac = 3          # Vaccination immunization period (The time to 
                                      # vaccinatization immunization after being vaccinated)
        self.param_n_exp = self.param_t_exp / self.param_dt
        self.param_n_inf = self.param_t_inf / self.param_dt
        self.param_n_vac = self.param_t_vac / self.param_dt
        
        self.param_save_res = 1
        self.param_disp_progress = 1
        self.param_disp_interval = 100
        self.param_vis_on = 1                  # Visualize results after simulation
        
        np.random.seed(1)
        self.param_rand_seed = np.random.randint(low = 1, high = 100, size = 625)
        
        # Define the initial values for the states
        self.init_susceptible = 9990
        self.init_exposed = 10
        self.init_quarantined = 0
        self.init_infected = 0
        self.init_isolated = 0
        self.init_vaccination_imm = 0
        self.init_maternally_imm = 0
        self.init_recovery_imm = 0
        
        # Define states
        self.states_x = [0, self.init_susceptible]
        self.states_dx = []
        self.states_name = ['Birth', 'Susceptible']
        self.states_type = ['Birth', 'Susceptible']
        
        # Define transitions
        self.source = ['Birth', 'Birth']
        self.dest = ['Susceptible', 'Maternally_Immunized' ]
        self.source_ind = []
        self.dest_ind = []
        
        
    def check_init(self):
        if self.param_beta_exp == 0 and self.param_beta_inf == 0:
            print('[ERROR] Both beta_exp and beta_inf cannot be zero.')
        elif self.param_beta_exp != 0 and self.param_beta_inf != 0:
            print('[ERROR] Both beta_exp and beta_inf cannot be non-zero.')
        else:
            print("[INFO] Initialization was done properly!")
            
            
    def create_states(self):
        
        # create some temporal variables
        n_vac = int(self.param_n_vac)
        n_vac_exp = n_vac + int(self.param_n_exp)
        n_vac_2exp = n_vac_exp + int(self.param_n_exp)
        n_vac_2exp_inf = n_vac_2exp + int(self.param_n_inf)
        n_vac_2exp_2inf = n_vac_2exp_inf + int(self.param_n_inf) + 1
        count = len(self.states_name) - 1
        
        # loop to create states
        while count < n_vac_2exp_2inf:
            # Vaccinated States
            if count <= n_vac:
                self.states_name.append('Vaccinated_{}'.format(count))
                self.states_type.append('Susceptible')
            # Exposed States (Includes both exposed and quarantined)
            elif count > n_vac and count <= n_vac_exp:
                self.states_name.append('Exposed_{}'.format(count - n_vac))
                self.states_type.append('Exposed')
                if count == n_vac + 1:
                    self.states_x.append(self.init_exposed)
                    count += 1
                    continue
            elif count > n_vac_exp and count <= n_vac_2exp:
                self.states_name.append('Quarantined_{}'.format(count - n_vac_exp))
                self.states_type.append('Exposed')
                if count == n_vac_exp + 1:
                    self.states_x.append(self.init_quarantined)
                    count += 1
                    continue
            # Infected States (Includes both infected and isolated)
            elif count > n_vac_2exp and count <= n_vac_2exp_inf:
                self.states_name.append('Infected_{}'.format(count - n_vac_2exp))
                self.states_type.append('Infected')
                if count == n_vac_2exp + 1:
                    self.states_x.append(self.init_infected)
                    count += 1
                    continue
            else:
                self.states_name.append('Isolated_{}'.format(count - n_vac_2exp_inf))
                self.states_type.append('Infected')
                if count == n_vac_2exp + 1:
                    self.states_x.append(self.init_isolated)
                    count += 1
                    continue
                
            self.states_x.append(0)
                
            count += 1
            
        # Add the Immunized and dead states
        self.states_name.append('Vaccination_Immunized')
        self.states_type.append('Immunized')
        self.states_x.append(self.init_vaccination_imm)

        self.states_name.append('Maternally_Immunized')
        self.states_type.append('Immunized')
        self.states_x.append(self.init_maternally_imm)

        self.states_name.append('Recovery_Immunized')
        self.states_type.append('Immunized')
        self.states_x.append(self.init_recovery_imm)

        self.states_name.append('Dead')
        self.states_type.append('Dead')
        self.states_x.append(0)
        
        # convert states into numpy arrays
        # for fast processing
        self.states_x = np.asarray(self.states_x, dtype=np.float32)
        self.states_dx = np.zeros(self.states_x.shape, dtype=np.float32)
        #self.states_name = np.asarray(self.states_name, dtype=str)
        #self.states_type = np.asarray(self.states_type, dtype=str)

        # initialize number of states
        self.param_num_states = len(self.states_x)
        
        print("[INFO] States were created...")
        
        
    def create_transitions(self):
        # create some temporal variables
        count = len(self.source) - 1
        n_st = self.param_num_states 
        n_vac = int(self.param_n_vac) 
        n_exp = int(self.param_n_exp) 
        n_inf = int(self.param_n_inf)
        
        # Transition 3 - Any State except Birth to Dead (Natural Mortality)
        for ind in range(count, n_st - 1):
            self.source.append(self.states_name[ind])
            self.dest.append('Dead')
            
        # Transition 4 - Susceptible to Vaccinated[1]
        if self.param_vr != 0:
            self.source.append('Susceptible')
            self.dest.append('Vaccinated_1')
            
        # Transition 5 - Vaccinated[i] to Vaccinated[i+1] until i+1 == n_vac
        if self.param_n_vac != 0:
            for ind in range(n_vac - 1):
                self.source.append(self.states_name[2 + ind])
                self.dest.append(self.states_name[3 + ind])
                
        if self.param_vr != 0:
            # Transition 6 - Vaccinated[n_vac] to Vaccination_Immunized
            self.source.append('Vaccinated_{}'.format(n_vac))
            self.dest.append('Vaccination_Immunized')
            
            # Transition 7 - Vaccinated[n_vac] to Susceptible
            self.source.append('Vaccinated_{}'.format(n_vac))
            self.dest.append('Susceptible')
            
            # Transition 8 - Susceptible to Exposed[1]
            if self.param_n_exp != 0:
                self.source.append('Susceptible')
                self.dest.append('Exposed_1')
                
            # Transition 9 - Susceptible to Infected[1]
            self.source.append('Susceptible')
            self.dest.append('Infected_1')
            
        # Transition 10 - Exposed[i] to Exposed[i+1] until i+1 == n_exp
        for ind in range(n_exp - 1):
            self.source.append('Exposed_{}'.format(ind + 1))
            self.dest.append('Exposed_{}'.format(ind + 2))
            
        # Transition 11 - Exposed[n_inc] to Infected[1]
        if self.param_n_exp != 0:
            self.source.append('Exposed_{}'.format(n_exp))
            self.dest.append('Infected_1')
            
        # Transition 12 - Exposed[i] to Quarantined[i+1] until i+1 == n_exp
        for ind in range(n_exp - 1):
            self.source.append('Exposed_{}'.format(ind + 1))
            self.dest.append('Quarantined_{}'.format(ind + 2))
            
        # Transition 13 - Quarantined[i] to Quarantined[i+1] until i+1 == n_exp
        for ind in range(n_exp - 1):
            self.source.append('Quarantined_{}'.format(ind + 1))
            self.dest.append('Quarantined_{}'.format(ind + 2))
            
        # Transition 14 - Quarantined[n_exp] to Isolated[1]
        if self.param_n_exp != 0:
            self.source.append('Quarantined_{}'.format(n_exp))
            self.dest.append('Isolated_1')
        
        # Transition 15 - Infected[i] to Infected[i+1] until i+1 == n_inf
        for ind in range(n_inf - 1):
            self.source.append('Infected_{}'.format(ind + 1))
            self.dest.append('Infected_{}'.format(ind + 2))
            
        # Transition 16 - Isolated[i] to Isolated[i+1] until i+1 == n_inf
        for ind in range(n_inf - 1):
            self.source.append('Isolated_{}'.format(ind + 1))
            self.dest.append('Isolated_{}'.format(ind + 2))
            
        # Transition 17 - Infected[i] to Isolated[i+1] until i+1 == n_inf
        for ind in range(n_inf - 1):
            self.source.append('Infected_{}'.format(ind + 1))
            self.dest.append('Isolated_{}'.format(ind + 2))
            
        # Transition 18 - Infected[n_inf] to Recovery_Immunized
        self.source.append('Infected_{}'.format(n_inf))
        self.dest.append('Recovery_Immunized')
        
        # Transition 19 - Isolated[n_inf] to Recovery Immunized
        self.source.append('Isolated_{}'.format(n_inf))
        self.dest.append('Recovery_Immunized')
        
        # Transition 20 - Infected[n_inf] to Susceptible
        self.source.append('Infected_{}'.format(n_inf))
        self.dest.append('Susceptible')
        
        # Transition 21 - Isolated[n_inf] to Susceptible
        self.source.append('Isolated_{}'.format(n_inf))
        self.dest.append('Susceptible')
        
        # Transition 22 - Infected[n_inf] to Dead
        self.source.append('Infected_{}'.format(n_inf))
        self.dest.append('Dead')
        
        # Transition 23 - Isolated[n_inf] to Dead
        self.source.append('Isolated_{}'.format(n_inf))
        self.dest.append('Dead')
        
        for ind in range(len(self.source)):
            self.source_ind.append(self.states_name.index(self.source[ind]))
            self.dest_ind.append(self.states_name.index(self.dest[ind]))

        print("[INFO] State transitions were created...")

        
    #def stoch_solver(self):
        
        
node = Node()
node.check_init()
node.create_states()
node.create_transitions()
#print(node.source)