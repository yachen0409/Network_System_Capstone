import random
import protocols
import matplotlib.pyplot as plt
class Setting():
    def __init__(self, host_num=3, total_time=10000, packet_num=500, packet_size=5, max_colision_wait_time=None, p_resend=None, coefficient=8, link_delay=1, seed=None) -> None:
        self.host_num = host_num # host 數量
        self.total_time = total_time # 模擬時間總長，時間以1為最小時間單位
        self.packet_num = packet_num # 每個 host 生成的封包數量
        # packet time是完成一個封包所需的時間，包含了送packet的link delay和ack的link delay
        # 假設等待ack的時間等同於link delay
        self.packet_time = packet_size + 2*link_delay # 每個封包完成所需要的時間，等同於slotted aloha的slot size
        if max_colision_wait_time is None:
            self.max_colision_wait_time = host_num * self.packet_time * coefficient# your answer
        else:
            self.max_colision_wait_time = max_colision_wait_time 
        if p_resend is None:
            self.p_resend = (1 / (host_num * coefficient))# your answer
        else:
            self.p_resend = p_resend 
        # self.max_colision_wait_time = max_colision_wait_time # ALOHA, CSMA, CSMA/cD 重新發送封包的最大等待時間
        # self.p_resend = p_resend # slotted aloha 每個slot開始時，重送封包的機率
        self.packet_size = packet_size
        self.link_delay = link_delay # link delay
        if seed is None:
            self.seed = random.randint(1, 10000)
        else:
            self.seed = seed # seed 用於 random，同樣的 seed 會有相同的結果

    # hosts產生封包的時間
    # e.g.
    #   [[10, 20, 30], # host 0
    #    [20, 30, 50], # host 1
    #    [30, 50, 60]] # host 2
    def gen_packets(self):
        random.seed(self.seed)
        packets = [[] for i in range(self.host_num)]
        for i in range(self.host_num):
            packets[i] = random.sample(range(1, self.total_time-self.packet_size), self.packet_num)
            packets[i].sort()
        return packets
    
def main():
    #TODO
    #! Code Test
    #? simple code tests
    setting = Setting(host_num=3, total_time=100, packet_num=4, max_colision_wait_time=20, p_resend=0.3, packet_size=3, link_delay=1, seed=109550073)
    aloha_s, aloha_i, aloha_c = protocols.aloha(setting, True)
    print('success rate:', aloha_s)
    print('idle rate:', aloha_i)
    print('collision rate:', aloha_c, end='\n\n')
    slotted_aloha_s, slotted_aloha_i, slotted_aloha_c = protocols.slotted_aloha(setting, True)
    print('success rate:', slotted_aloha_s)
    print('idle rate:', slotted_aloha_i)
    print('collision rate:', slotted_aloha_c, end='\n\n')
    csma_s, csma_i, csma_c = protocols.csma(setting, True)
    print('success rate:', csma_s)
    print('idle rate:', csma_i)
    print('collision rate:', csma_c, end='\n\n')
    csma_cd_s, csma_cd_i, csma_cd_c = protocols.csma_cd(setting, True)
    print('success rate:', csma_cd_s)
    print('idle rate:', csma_cd_i)
    print('collision rate:', csma_cd_c, end='\n')
    #! QUESTIONS 
    #? set setting and run simulation
    test_times=20
    aloha_s_list = []
    slotted_aloha_s_list = []
    csma_s_list = []
    csma_cd_s_list = []
    aloha_i_list = []
    slotted_aloha_i_list = []
    csma_i_list = []
    csma_cd_i_list = []
    aloha_c_list = []
    slotted_aloha_c_list = []
    csma_c_list = []
    csma_cd_c_list = []
    #! q1
    print('Processing Q1......')
    host_num_list = [2,3,4,6]
    packet_num_list = [1200,800,600,400] 
    for i in range(test_times):
        tmp_aloha_s_list = []
        tmp_aloha_i_list = []
        tmp_aloha_c_list = []
        tmp_slotted_aloha_s_list = []
        tmp_slotted_aloha_i_list = []
        tmp_slotted_aloha_c_list = []
        tmp_csma_s_list = []
        tmp_csma_cd_s_list = []
        tmp_csma_i_list = []
        tmp_csma_cd_i_list = []
        tmp_csma_c_list = []
        tmp_csma_cd_c_list = []
        for h,p in zip(host_num_list, packet_num_list):
            setting = Setting(host_num=h, packet_num=p, max_colision_wait_time=20, p_resend=0.3)
            aloha_s, aloha_i, aloha_c = protocols.aloha(setting, False)
            slotted_aloha_s, slotted_aloha_i, slotted_aloha_c = protocols.slotted_aloha(setting, False)
            csma_s, csma_i, csma_c = protocols.csma(setting, False)
            csma_cd_s, csma_cd_i, csma_cd_c = protocols.csma_cd(setting, False)
            tmp_aloha_s_list.append(aloha_s)
            tmp_aloha_i_list.append(aloha_i)
            tmp_aloha_c_list.append(aloha_c)
            tmp_slotted_aloha_s_list.append(slotted_aloha_s)
            tmp_slotted_aloha_i_list.append(slotted_aloha_i)
            tmp_slotted_aloha_c_list.append(slotted_aloha_c)
            tmp_csma_s_list.append(csma_s)
            tmp_csma_cd_s_list.append(csma_cd_s)
            tmp_csma_i_list.append(csma_i)
            tmp_csma_cd_i_list.append(csma_cd_i)
            tmp_csma_c_list.append(csma_c)
            tmp_csma_cd_c_list.append(csma_cd_c)
        if len(aloha_s_list) == 0:
            aloha_s_list = [0 for i in range(len(tmp_aloha_s_list))];
        if len(aloha_i_list) == 0:
                aloha_i_list = [0 for i in range(len(tmp_aloha_i_list))];
        if len(aloha_c_list) == 0:
                aloha_c_list = [0 for i in range(len(tmp_aloha_c_list))];
        if len(slotted_aloha_s_list) == 0:
            slotted_aloha_s_list = [0 for i in range(len(tmp_slotted_aloha_s_list))];
        if len(slotted_aloha_i_list) == 0:
                slotted_aloha_i_list = [0 for i in range(len(tmp_slotted_aloha_i_list))];
        if len(slotted_aloha_c_list) == 0:
                slotted_aloha_c_list = [0 for i in range(len(tmp_slotted_aloha_c_list))];
        if len(csma_s_list) == 0:
            csma_s_list = [0 for i in range(len(tmp_csma_s_list))];
        if len(csma_i_list) == 0:
                csma_i_list = [0 for i in range(len(tmp_csma_i_list))];
        if len(csma_c_list) == 0:
                csma_c_list = [0 for i in range(len(tmp_csma_c_list))];
        if len(csma_cd_s_list) == 0:
            csma_cd_s_list = [0 for i in range(len(tmp_csma_cd_s_list))];
        if len(csma_cd_i_list) == 0:
                csma_cd_i_list = [0 for i in range(len(tmp_csma_cd_i_list))];
        if len(csma_cd_c_list) == 0:
                csma_cd_c_list = [0 for i in range(len(tmp_csma_cd_c_list))];
        aloha_s_list = [aloha_s_list[i] + tmp_aloha_s_list[i] for i in range(len(tmp_aloha_s_list))]
        aloha_i_list = [aloha_i_list[i] + tmp_aloha_i_list[i] for i in range(len(tmp_aloha_i_list))]
        aloha_c_list = [aloha_c_list[i] + tmp_aloha_c_list[i] for i in range(len(tmp_aloha_c_list))]
        slotted_aloha_s_list = [slotted_aloha_s_list[i] + tmp_slotted_aloha_s_list[i] for i in range(len(tmp_slotted_aloha_s_list))]
        slotted_aloha_i_list = [slotted_aloha_i_list[i] + tmp_slotted_aloha_i_list[i] for i in range(len(tmp_slotted_aloha_i_list))]
        slotted_aloha_c_list = [slotted_aloha_c_list[i] + tmp_slotted_aloha_c_list[i] for i in range(len(tmp_slotted_aloha_c_list))]
        csma_s_list = [csma_s_list[i] + tmp_csma_s_list[i] for i in range(len(tmp_csma_s_list))]
        csma_i_list = [csma_i_list[i] + tmp_csma_i_list[i] for i in range(len(tmp_csma_i_list))]
        csma_c_list = [csma_c_list[i] + tmp_csma_c_list[i] for i in range(len(tmp_csma_c_list))]
        csma_cd_s_list = [csma_cd_s_list[i] + tmp_csma_cd_s_list[i] for i in range(len(tmp_csma_cd_s_list))]
        csma_cd_i_list = [csma_cd_i_list[i] + tmp_csma_cd_i_list[i] for i in range(len(tmp_csma_cd_i_list))]
        csma_cd_c_list = [csma_cd_c_list[i] + tmp_csma_cd_c_list[i] for i in range(len(tmp_csma_cd_c_list))]
    # Plot the data
    aloha_s_list = [aloha_s_list[i]/test_times for i in range(len(aloha_s_list))]
    aloha_i_list = [aloha_i_list[i]/test_times for i in range(len(aloha_i_list))]
    aloha_c_list = [aloha_c_list[i]/test_times for i in range(len(aloha_c_list))]
    slotted_aloha_s_list = [slotted_aloha_s_list[i]/test_times for i in range(len(slotted_aloha_s_list))]
    slotted_aloha_i_list = [slotted_aloha_i_list[i]/test_times for i in range(len(slotted_aloha_i_list))]
    slotted_aloha_c_list = [slotted_aloha_c_list[i]/test_times for i in range(len(slotted_aloha_c_list))]
    csma_s_list = [csma_s_list[i]/test_times for i in range(len(csma_s_list))]
    csma_i_list = [csma_i_list[i]/test_times for i in range(len(csma_i_list))]
    csma_c_list = [csma_c_list[i]/test_times for i in range(len(csma_c_list))]
    csma_cd_s_list = [csma_cd_s_list[i]/test_times for i in range(len(csma_cd_s_list))]
    csma_cd_i_list = [csma_cd_i_list[i]/test_times for i in range(len(csma_cd_i_list))]
    csma_cd_c_list = [csma_cd_c_list[i]/test_times for i in range(len(csma_cd_c_list))]
    tick_locs = host_num_list
    tick_labels = [str(x) for x in host_num_list]
    plt.plot(host_num_list, aloha_s_list, label='ALOHA', marker='x', color='k')
    plt.plot(host_num_list, slotted_aloha_s_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(host_num_list, csma_s_list, label='CSMA', marker='^', color='g')
    plt.plot(host_num_list, csma_cd_s_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Number of Hosts')
    plt.ylabel('Success Rate')
    plt.title("Influence of Host Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q1/success_rate_1.png")
    plt.cla()
    plt.clf()
    plt.plot(host_num_list, aloha_i_list, label='ALOHA', marker='x', color='k')
    plt.plot(host_num_list, slotted_aloha_i_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(host_num_list, csma_i_list, label='CSMA', marker='^', color='g')
    plt.plot(host_num_list, csma_cd_i_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Number of Hosts')
    plt.ylabel('Idle Rate')
    plt.title("Influence of Host Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q1/idle_rate_1.png")
    plt.cla()
    plt.clf()
    plt.plot(host_num_list, aloha_c_list, label='ALOHA', marker='x', color='k')
    plt.plot(host_num_list, slotted_aloha_c_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(host_num_list, csma_c_list, label='CSMA', marker='^', color='g')
    plt.plot(host_num_list, csma_cd_c_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Number of Hosts')
    plt.ylabel('Collision Rate')
    plt.title("Influence of Host Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q1/collision_rate_1.png")
    plt.cla()
    plt.clf()
    print('Q1 Done!')
    #!q3
    print('Processing Q3......')
    aloha_s_list.clear()
    slotted_aloha_s_list.clear()
    csma_s_list.clear()
    csma_cd_s_list.clear()
    aloha_i_list.clear()
    slotted_aloha_i_list.clear()
    csma_i_list.clear()
    csma_cd_i_list.clear()
    aloha_c_list.clear()
    slotted_aloha_c_list.clear()
    csma_c_list.clear()
    csma_cd_c_list.clear()
    # host_num_list.clear()
    for i in range(test_times):
        tmp_aloha_s_list = []
        tmp_aloha_i_list = []
        tmp_aloha_c_list = []
        tmp_slotted_aloha_s_list = []
        tmp_slotted_aloha_i_list = []
        tmp_slotted_aloha_c_list = []
        tmp_csma_s_list = []
        tmp_csma_cd_s_list = []
        tmp_csma_i_list = []
        tmp_csma_cd_i_list = []
        tmp_csma_c_list = []
        tmp_csma_cd_c_list = []
        for h,p in zip(host_num_list, packet_num_list):
            setting = Setting(host_num=h, packet_num=p, coefficient=8)
            aloha_s, aloha_i, aloha_c = protocols.aloha(setting, False)
            # print("seed =", setting.seed)
            # print("aloha, max_colision_wait_time =", setting.max_colision_wait_time)
            slotted_aloha_s, slotted_aloha_i, slotted_aloha_c = protocols.slotted_aloha(setting, False)
            # print("slotted_aloha, p_resend =", setting.p_resend)
            csma_s, csma_i, csma_c = protocols.csma(setting, False)
            csma_cd_s, csma_cd_i, csma_cd_c = protocols.csma_cd(setting, False)
            tmp_aloha_s_list.append(aloha_s)
            tmp_aloha_i_list.append(aloha_i)
            tmp_aloha_c_list.append(aloha_c)
            tmp_slotted_aloha_s_list.append(slotted_aloha_s)
            tmp_slotted_aloha_i_list.append(slotted_aloha_i)
            tmp_slotted_aloha_c_list.append(slotted_aloha_c)
            tmp_csma_s_list.append(csma_s)
            tmp_csma_cd_s_list.append(csma_cd_s)
            tmp_csma_i_list.append(csma_i)
            tmp_csma_cd_i_list.append(csma_cd_i)
            tmp_csma_c_list.append(csma_c)
            tmp_csma_cd_c_list.append(csma_cd_c)
        if len(aloha_s_list) == 0:
            aloha_s_list = [0 for i in range(len(tmp_aloha_s_list))];
        if len(aloha_i_list) == 0:
                aloha_i_list = [0 for i in range(len(tmp_aloha_i_list))];
        if len(aloha_c_list) == 0:
                aloha_c_list = [0 for i in range(len(tmp_aloha_c_list))];
        if len(slotted_aloha_s_list) == 0:
            slotted_aloha_s_list = [0 for i in range(len(tmp_slotted_aloha_s_list))];
        if len(slotted_aloha_i_list) == 0:
                slotted_aloha_i_list = [0 for i in range(len(tmp_slotted_aloha_i_list))];
        if len(slotted_aloha_c_list) == 0:
                slotted_aloha_c_list = [0 for i in range(len(tmp_slotted_aloha_c_list))];
        if len(csma_s_list) == 0:
            csma_s_list = [0 for i in range(len(tmp_csma_s_list))];
        if len(csma_i_list) == 0:
                csma_i_list = [0 for i in range(len(tmp_csma_i_list))];
        if len(csma_c_list) == 0:
                csma_c_list = [0 for i in range(len(tmp_csma_c_list))];
        if len(csma_cd_s_list) == 0:
            csma_cd_s_list = [0 for i in range(len(tmp_csma_cd_s_list))];
        if len(csma_cd_i_list) == 0:
                csma_cd_i_list = [0 for i in range(len(tmp_csma_cd_i_list))];
        if len(csma_cd_c_list) == 0:
                csma_cd_c_list = [0 for i in range(len(tmp_csma_cd_c_list))];
        aloha_s_list = [aloha_s_list[i] + tmp_aloha_s_list[i] for i in range(len(tmp_aloha_s_list))]
        aloha_i_list = [aloha_i_list[i] + tmp_aloha_i_list[i] for i in range(len(tmp_aloha_i_list))]
        aloha_c_list = [aloha_c_list[i] + tmp_aloha_c_list[i] for i in range(len(tmp_aloha_c_list))]
        slotted_aloha_s_list = [slotted_aloha_s_list[i] + tmp_slotted_aloha_s_list[i] for i in range(len(tmp_slotted_aloha_s_list))]
        slotted_aloha_i_list = [slotted_aloha_i_list[i] + tmp_slotted_aloha_i_list[i] for i in range(len(tmp_slotted_aloha_i_list))]
        slotted_aloha_c_list = [slotted_aloha_c_list[i] + tmp_slotted_aloha_c_list[i] for i in range(len(tmp_slotted_aloha_c_list))]
        csma_s_list = [csma_s_list[i] + tmp_csma_s_list[i] for i in range(len(tmp_csma_s_list))]
        csma_i_list = [csma_i_list[i] + tmp_csma_i_list[i] for i in range(len(tmp_csma_i_list))]
        csma_c_list = [csma_c_list[i] + tmp_csma_c_list[i] for i in range(len(tmp_csma_c_list))]
        csma_cd_s_list = [csma_cd_s_list[i] + tmp_csma_cd_s_list[i] for i in range(len(tmp_csma_cd_s_list))]
        csma_cd_i_list = [csma_cd_i_list[i] + tmp_csma_cd_i_list[i] for i in range(len(tmp_csma_cd_i_list))]
        csma_cd_c_list = [csma_cd_c_list[i] + tmp_csma_cd_c_list[i] for i in range(len(tmp_csma_cd_c_list))]
    # Plot the data
    aloha_s_list = [aloha_s_list[i]/test_times for i in range(len(aloha_s_list))]
    aloha_i_list = [aloha_i_list[i]/test_times for i in range(len(aloha_i_list))]
    aloha_c_list = [aloha_c_list[i]/test_times for i in range(len(aloha_c_list))]
    slotted_aloha_s_list = [slotted_aloha_s_list[i]/test_times for i in range(len(slotted_aloha_s_list))]
    slotted_aloha_i_list = [slotted_aloha_i_list[i]/test_times for i in range(len(slotted_aloha_i_list))]
    slotted_aloha_c_list = [slotted_aloha_c_list[i]/test_times for i in range(len(slotted_aloha_c_list))]
    csma_s_list = [csma_s_list[i]/test_times for i in range(len(csma_s_list))]
    csma_i_list = [csma_i_list[i]/test_times for i in range(len(csma_i_list))]
    csma_c_list = [csma_c_list[i]/test_times for i in range(len(csma_c_list))]
    csma_cd_s_list = [csma_cd_s_list[i]/test_times for i in range(len(csma_cd_s_list))]
    csma_cd_i_list = [csma_cd_i_list[i]/test_times for i in range(len(csma_cd_i_list))]
    csma_cd_c_list = [csma_cd_c_list[i]/test_times for i in range(len(csma_cd_c_list))]
    tick_locs = host_num_list
    tick_labels = [str(x) for x in host_num_list]
    plt.plot(host_num_list, aloha_s_list, label='ALOHA', marker='x', color='k')
    plt.plot(host_num_list, slotted_aloha_s_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(host_num_list, csma_s_list, label='CSMA', marker='^', color='g')
    plt.plot(host_num_list, csma_cd_s_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Number of Hosts')
    plt.ylabel('Success Rate')
    plt.title("Influence of Host Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q3/success_rate_3.png")
    plt.cla()
    plt.clf()
    plt.plot(host_num_list, aloha_i_list, label='ALOHA', marker='x', color='k')
    plt.plot(host_num_list, slotted_aloha_i_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(host_num_list, csma_i_list, label='CSMA', marker='^', color='g')
    plt.plot(host_num_list, csma_cd_i_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Number of Hosts')
    plt.ylabel('Idle Rate')
    plt.title("Influence of Host Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q3/idle_rate_3.png")
    plt.cla()
    plt.clf()
    plt.plot(host_num_list, aloha_c_list, label='ALOHA', marker='x', color='k')
    plt.plot(host_num_list, slotted_aloha_c_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(host_num_list, csma_c_list, label='CSMA', marker='^', color='g')
    plt.plot(host_num_list, csma_cd_c_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Number of Hosts')
    plt.ylabel('Collision Rate')
    plt.title("Influence of Host Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q3/collision_rate_3.png")
    plt.cla()
    plt.clf()
    print('Q3 Done!')
    #!q4
    print('Processing Q4......')
    aloha_s_list.clear()
    slotted_aloha_s_list.clear()
    csma_s_list.clear()
    csma_cd_s_list.clear()
    aloha_i_list.clear()
    slotted_aloha_i_list.clear()
    csma_i_list.clear()
    csma_cd_i_list.clear()
    aloha_c_list.clear()
    slotted_aloha_c_list.clear()
    csma_c_list.clear()
    csma_cd_c_list.clear()
    c_list = []
    for i in range(test_times):
        tmp_aloha_s_list = []
        tmp_aloha_i_list = []
        tmp_aloha_c_list = []
        tmp_slotted_aloha_s_list = []
        tmp_slotted_aloha_i_list = []
        tmp_slotted_aloha_c_list = []
        tmp_csma_s_list = []
        tmp_csma_cd_s_list = []
        tmp_csma_i_list = []
        tmp_csma_cd_i_list = []
        tmp_csma_c_list = []
        tmp_csma_cd_c_list = []
        for c in range(1, 31, 1):
            setting = Setting(coefficient=c)
            aloha_s, aloha_i, aloha_c = protocols.aloha(setting, False)
            slotted_aloha_s, slotted_aloha_i, slotted_aloha_c = protocols.slotted_aloha(setting, False)
            csma_s, csma_i, csma_c = protocols.csma(setting, False)
            csma_cd_s, csma_cd_i, csma_cd_c = protocols.csma_cd(setting, False)
            tmp_aloha_s_list.append(aloha_s)
            tmp_aloha_i_list.append(aloha_i)
            tmp_aloha_c_list.append(aloha_c)
            tmp_slotted_aloha_s_list.append(slotted_aloha_s)
            tmp_slotted_aloha_i_list.append(slotted_aloha_i)
            tmp_slotted_aloha_c_list.append(slotted_aloha_c)
            tmp_csma_s_list.append(csma_s)
            tmp_csma_cd_s_list.append(csma_cd_s)
            tmp_csma_i_list.append(csma_i)
            tmp_csma_cd_i_list.append(csma_cd_i)
            tmp_csma_c_list.append(csma_c)
            tmp_csma_cd_c_list.append(csma_cd_c)
            if i == 0:
                c_list.append(c)
        if len(aloha_s_list) == 0:
            aloha_s_list = [0 for i in range(len(tmp_aloha_s_list))];
        if len(aloha_i_list) == 0:
                aloha_i_list = [0 for i in range(len(tmp_aloha_i_list))];
        if len(aloha_c_list) == 0:
                aloha_c_list = [0 for i in range(len(tmp_aloha_c_list))];
        if len(slotted_aloha_s_list) == 0:
            slotted_aloha_s_list = [0 for i in range(len(tmp_slotted_aloha_s_list))];
        if len(slotted_aloha_i_list) == 0:
                slotted_aloha_i_list = [0 for i in range(len(tmp_slotted_aloha_i_list))];
        if len(slotted_aloha_c_list) == 0:
                slotted_aloha_c_list = [0 for i in range(len(tmp_slotted_aloha_c_list))];
        if len(csma_s_list) == 0:
            csma_s_list = [0 for i in range(len(tmp_csma_s_list))];
        if len(csma_i_list) == 0:
                csma_i_list = [0 for i in range(len(tmp_csma_i_list))];
        if len(csma_c_list) == 0:
                csma_c_list = [0 for i in range(len(tmp_csma_c_list))];
        if len(csma_cd_s_list) == 0:
            csma_cd_s_list = [0 for i in range(len(tmp_csma_cd_s_list))];
        if len(csma_cd_i_list) == 0:
                csma_cd_i_list = [0 for i in range(len(tmp_csma_cd_i_list))];
        if len(csma_cd_c_list) == 0:
                csma_cd_c_list = [0 for i in range(len(tmp_csma_cd_c_list))];
        aloha_s_list = [aloha_s_list[i] + tmp_aloha_s_list[i] for i in range(len(tmp_aloha_s_list))]
        aloha_i_list = [aloha_i_list[i] + tmp_aloha_i_list[i] for i in range(len(tmp_aloha_i_list))]
        aloha_c_list = [aloha_c_list[i] + tmp_aloha_c_list[i] for i in range(len(tmp_aloha_c_list))]
        slotted_aloha_s_list = [slotted_aloha_s_list[i] + tmp_slotted_aloha_s_list[i] for i in range(len(tmp_slotted_aloha_s_list))]
        slotted_aloha_i_list = [slotted_aloha_i_list[i] + tmp_slotted_aloha_i_list[i] for i in range(len(tmp_slotted_aloha_i_list))]
        slotted_aloha_c_list = [slotted_aloha_c_list[i] + tmp_slotted_aloha_c_list[i] for i in range(len(tmp_slotted_aloha_c_list))]
        csma_s_list = [csma_s_list[i] + tmp_csma_s_list[i] for i in range(len(tmp_csma_s_list))]
        csma_i_list = [csma_i_list[i] + tmp_csma_i_list[i] for i in range(len(tmp_csma_i_list))]
        csma_c_list = [csma_c_list[i] + tmp_csma_c_list[i] for i in range(len(tmp_csma_c_list))]
        csma_cd_s_list = [csma_cd_s_list[i] + tmp_csma_cd_s_list[i] for i in range(len(tmp_csma_cd_s_list))]
        csma_cd_i_list = [csma_cd_i_list[i] + tmp_csma_cd_i_list[i] for i in range(len(tmp_csma_cd_i_list))]
        csma_cd_c_list = [csma_cd_c_list[i] + tmp_csma_cd_c_list[i] for i in range(len(tmp_csma_cd_c_list))]
    # Plot the data
    aloha_s_list = [aloha_s_list[i]/test_times for i in range(len(aloha_s_list))]
    aloha_i_list = [aloha_i_list[i]/test_times for i in range(len(aloha_i_list))]
    aloha_c_list = [aloha_c_list[i]/test_times for i in range(len(aloha_c_list))]
    slotted_aloha_s_list = [slotted_aloha_s_list[i]/test_times for i in range(len(slotted_aloha_s_list))]
    slotted_aloha_i_list = [slotted_aloha_i_list[i]/test_times for i in range(len(slotted_aloha_i_list))]
    slotted_aloha_c_list = [slotted_aloha_c_list[i]/test_times for i in range(len(slotted_aloha_c_list))]
    csma_s_list = [csma_s_list[i]/test_times for i in range(len(csma_s_list))]
    csma_i_list = [csma_i_list[i]/test_times for i in range(len(csma_i_list))]
    csma_c_list = [csma_c_list[i]/test_times for i in range(len(csma_c_list))]
    csma_cd_s_list = [csma_cd_s_list[i]/test_times for i in range(len(csma_cd_s_list))]
    csma_cd_i_list = [csma_cd_i_list[i]/test_times for i in range(len(csma_cd_i_list))]
    csma_cd_c_list = [csma_cd_c_list[i]/test_times for i in range(len(csma_cd_c_list))]
    tick_locs = c_list
    tick_labels = [str(x) for x in c_list]
    plt.plot(c_list, aloha_s_list, label='ALOHA', marker='x', color='k')
    plt.plot(c_list, slotted_aloha_s_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(c_list, csma_s_list, label='CSMA', marker='^', color='g')
    plt.plot(c_list, csma_cd_s_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Coefficient')
    plt.ylabel('Success Rate')
    plt.title("Influence of Coefficient")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q4/success_rate_4.png")
    plt.cla()
    plt.clf()
    plt.plot(c_list, aloha_i_list, label='ALOHA', marker='x', color='k')
    plt.plot(c_list, slotted_aloha_i_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(c_list, csma_i_list, label='CSMA', marker='^', color='g')
    plt.plot(c_list, csma_cd_i_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Coefficient')
    plt.ylabel('Idle Rate')
    plt.title("Influence of Coefficient")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q4/idle_rate_4.png")
    plt.cla()
    plt.clf()
    plt.plot(c_list, aloha_c_list, label='ALOHA', marker='x', color='k')
    plt.plot(c_list, slotted_aloha_c_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(c_list, csma_c_list, label='CSMA', marker='^', color='g')
    plt.plot(c_list, csma_cd_c_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Coefficient')
    plt.ylabel('Collision Rate')
    plt.title("Influence of Coefficient")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q4/collision_rate_4.png")
    plt.cla()
    plt.clf()
    print('Q4 Done!')
    #!q5
    print('Processing Q5......')
    aloha_s_list.clear()
    slotted_aloha_s_list.clear()
    csma_s_list.clear()
    csma_cd_s_list.clear()
    aloha_i_list.clear()
    slotted_aloha_i_list.clear()
    csma_i_list.clear()
    csma_cd_i_list.clear()
    aloha_c_list.clear()
    slotted_aloha_c_list.clear()
    csma_c_list.clear()
    csma_cd_c_list.clear()
    p_list = []
    for i in range(test_times):
        tmp_aloha_s_list = []
        tmp_aloha_i_list = []
        tmp_aloha_c_list = []
        tmp_slotted_aloha_s_list = []
        tmp_slotted_aloha_i_list = []
        tmp_slotted_aloha_c_list = []
        tmp_csma_s_list = []
        tmp_csma_cd_s_list = []
        tmp_csma_i_list = []
        tmp_csma_cd_i_list = []
        tmp_csma_c_list = []
        tmp_csma_cd_c_list = []
        for p in range(100, 1050, 50):
            setting = Setting(packet_num=p)
            aloha_s, aloha_i, aloha_c = protocols.aloha(setting, False)
            slotted_aloha_s, slotted_aloha_i, slotted_aloha_c = protocols.slotted_aloha(setting, False)
            csma_s, csma_i, csma_c = protocols.csma(setting, False)
            csma_cd_s, csma_cd_i, csma_cd_c = protocols.csma_cd(setting, False)
            tmp_aloha_s_list.append(aloha_s)
            tmp_aloha_i_list.append(aloha_i)
            tmp_aloha_c_list.append(aloha_c)
            tmp_slotted_aloha_s_list.append(slotted_aloha_s)
            tmp_slotted_aloha_i_list.append(slotted_aloha_i)
            tmp_slotted_aloha_c_list.append(slotted_aloha_c)
            tmp_csma_s_list.append(csma_s)
            tmp_csma_cd_s_list.append(csma_cd_s)
            tmp_csma_i_list.append(csma_i)
            tmp_csma_cd_i_list.append(csma_cd_i)
            tmp_csma_c_list.append(csma_c)
            tmp_csma_cd_c_list.append(csma_cd_c)
            if i == 0:
                p_list.append(p)
        if len(aloha_s_list) == 0:
            aloha_s_list = [0 for i in range(len(tmp_aloha_s_list))];
        if len(aloha_i_list) == 0:
                aloha_i_list = [0 for i in range(len(tmp_aloha_i_list))];
        if len(aloha_c_list) == 0:
                aloha_c_list = [0 for i in range(len(tmp_aloha_c_list))];
        if len(slotted_aloha_s_list) == 0:
            slotted_aloha_s_list = [0 for i in range(len(tmp_slotted_aloha_s_list))];
        if len(slotted_aloha_i_list) == 0:
                slotted_aloha_i_list = [0 for i in range(len(tmp_slotted_aloha_i_list))];
        if len(slotted_aloha_c_list) == 0:
                slotted_aloha_c_list = [0 for i in range(len(tmp_slotted_aloha_c_list))];
        if len(csma_s_list) == 0:
            csma_s_list = [0 for i in range(len(tmp_csma_s_list))];
        if len(csma_i_list) == 0:
                csma_i_list = [0 for i in range(len(tmp_csma_i_list))];
        if len(csma_c_list) == 0:
                csma_c_list = [0 for i in range(len(tmp_csma_c_list))];
        if len(csma_cd_s_list) == 0:
            csma_cd_s_list = [0 for i in range(len(tmp_csma_cd_s_list))];
        if len(csma_cd_i_list) == 0:
                csma_cd_i_list = [0 for i in range(len(tmp_csma_cd_i_list))];
        if len(csma_cd_c_list) == 0:
                csma_cd_c_list = [0 for i in range(len(tmp_csma_cd_c_list))];
        aloha_s_list = [aloha_s_list[i] + tmp_aloha_s_list[i] for i in range(len(tmp_aloha_s_list))]
        aloha_i_list = [aloha_i_list[i] + tmp_aloha_i_list[i] for i in range(len(tmp_aloha_i_list))]
        aloha_c_list = [aloha_c_list[i] + tmp_aloha_c_list[i] for i in range(len(tmp_aloha_c_list))]
        slotted_aloha_s_list = [slotted_aloha_s_list[i] + tmp_slotted_aloha_s_list[i] for i in range(len(tmp_slotted_aloha_s_list))]
        slotted_aloha_i_list = [slotted_aloha_i_list[i] + tmp_slotted_aloha_i_list[i] for i in range(len(tmp_slotted_aloha_i_list))]
        slotted_aloha_c_list = [slotted_aloha_c_list[i] + tmp_slotted_aloha_c_list[i] for i in range(len(tmp_slotted_aloha_c_list))]
        csma_s_list = [csma_s_list[i] + tmp_csma_s_list[i] for i in range(len(tmp_csma_s_list))]
        csma_i_list = [csma_i_list[i] + tmp_csma_i_list[i] for i in range(len(tmp_csma_i_list))]
        csma_c_list = [csma_c_list[i] + tmp_csma_c_list[i] for i in range(len(tmp_csma_c_list))]
        csma_cd_s_list = [csma_cd_s_list[i] + tmp_csma_cd_s_list[i] for i in range(len(tmp_csma_cd_s_list))]
        csma_cd_i_list = [csma_cd_i_list[i] + tmp_csma_cd_i_list[i] for i in range(len(tmp_csma_cd_i_list))]
        csma_cd_c_list = [csma_cd_c_list[i] + tmp_csma_cd_c_list[i] for i in range(len(tmp_csma_cd_c_list))]
    # Plot the data
    aloha_s_list = [aloha_s_list[i]/test_times for i in range(len(aloha_s_list))]
    aloha_i_list = [aloha_i_list[i]/test_times for i in range(len(aloha_i_list))]
    aloha_c_list = [aloha_c_list[i]/test_times for i in range(len(aloha_c_list))]
    slotted_aloha_s_list = [slotted_aloha_s_list[i]/test_times for i in range(len(slotted_aloha_s_list))]
    slotted_aloha_i_list = [slotted_aloha_i_list[i]/test_times for i in range(len(slotted_aloha_i_list))]
    slotted_aloha_c_list = [slotted_aloha_c_list[i]/test_times for i in range(len(slotted_aloha_c_list))]
    csma_s_list = [csma_s_list[i]/test_times for i in range(len(csma_s_list))]
    csma_i_list = [csma_i_list[i]/test_times for i in range(len(csma_i_list))]
    csma_c_list = [csma_c_list[i]/test_times for i in range(len(csma_c_list))]
    csma_cd_s_list = [csma_cd_s_list[i]/test_times for i in range(len(csma_cd_s_list))]
    csma_cd_i_list = [csma_cd_i_list[i]/test_times for i in range(len(csma_cd_i_list))]
    csma_cd_c_list = [csma_cd_c_list[i]/test_times for i in range(len(csma_cd_c_list))]
    tick_locs = p_list
    tick_labels = [str(x) for x in p_list]
    plt.plot(p_list, aloha_s_list, label='ALOHA', marker='x', color='k')
    plt.plot(p_list, slotted_aloha_s_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(p_list, csma_s_list, label='CSMA', marker='^', color='g')
    plt.plot(p_list, csma_cd_s_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Packet Num')
    plt.ylabel('Success Rate')
    plt.title("Influence of Packet Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q5/success_rate_5.png")
    plt.cla()
    plt.clf()
    plt.plot(p_list, aloha_i_list, label='ALOHA', marker='x', color='k')
    plt.plot(p_list, slotted_aloha_i_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(p_list, csma_i_list, label='CSMA', marker='^', color='g')
    plt.plot(p_list, csma_cd_i_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Packet Num')
    plt.ylabel('Idle Rate')
    plt.title("Influence of Packet Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q5/idle_rate_5.png")
    plt.cla()
    plt.clf()
    plt.plot(p_list, aloha_c_list, label='ALOHA', marker='x', color='k')
    plt.plot(p_list, slotted_aloha_c_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(p_list, csma_c_list, label='CSMA', marker='^', color='g')
    plt.plot(p_list, csma_cd_c_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Packet Num')
    plt.ylabel('Collision Rate')
    plt.title("Influence of Packet Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q5/collision_rate_5.png")
    plt.cla()
    plt.clf()
    print('Q5 Done!')
    #!q6
    print('Processing Q6......')
    aloha_s_list.clear()
    slotted_aloha_s_list.clear()
    csma_s_list.clear()
    csma_cd_s_list.clear()
    aloha_i_list.clear()
    slotted_aloha_i_list.clear()
    csma_i_list.clear()
    csma_cd_i_list.clear()
    aloha_c_list.clear()
    slotted_aloha_c_list.clear()
    csma_c_list.clear()
    csma_cd_c_list.clear()
    h_list = []
    for i in range(test_times):
        tmp_aloha_s_list = []
        tmp_aloha_i_list = []
        tmp_aloha_c_list = []
        tmp_slotted_aloha_s_list = []
        tmp_slotted_aloha_i_list = []
        tmp_slotted_aloha_c_list = []
        tmp_csma_s_list = []
        tmp_csma_cd_s_list = []
        tmp_csma_i_list = []
        tmp_csma_cd_i_list = []
        tmp_csma_c_list = []
        tmp_csma_cd_c_list = []
        for h in range(1, 11, 1):
            setting = Setting(host_num=h)
            aloha_s, aloha_i, aloha_c = protocols.aloha(setting, False)
            slotted_aloha_s, slotted_aloha_i, slotted_aloha_c = protocols.slotted_aloha(setting, False)
            csma_s, csma_i, csma_c = protocols.csma(setting, False)
            csma_cd_s, csma_cd_i, csma_cd_c = protocols.csma_cd(setting, False)
            tmp_aloha_s_list.append(aloha_s)
            tmp_aloha_i_list.append(aloha_i)
            tmp_aloha_c_list.append(aloha_c)
            tmp_slotted_aloha_s_list.append(slotted_aloha_s)
            tmp_slotted_aloha_i_list.append(slotted_aloha_i)
            tmp_slotted_aloha_c_list.append(slotted_aloha_c)
            tmp_csma_s_list.append(csma_s)
            tmp_csma_cd_s_list.append(csma_cd_s)
            tmp_csma_i_list.append(csma_i)
            tmp_csma_cd_i_list.append(csma_cd_i)
            tmp_csma_c_list.append(csma_c)
            tmp_csma_cd_c_list.append(csma_cd_c)
            if i == 0:
                h_list.append(h)
        if len(aloha_s_list) == 0:
            aloha_s_list = [0 for i in range(len(tmp_aloha_s_list))];
        if len(aloha_i_list) == 0:
                aloha_i_list = [0 for i in range(len(tmp_aloha_i_list))];
        if len(aloha_c_list) == 0:
                aloha_c_list = [0 for i in range(len(tmp_aloha_c_list))];
        if len(slotted_aloha_s_list) == 0:
            slotted_aloha_s_list = [0 for i in range(len(tmp_slotted_aloha_s_list))];
        if len(slotted_aloha_i_list) == 0:
                slotted_aloha_i_list = [0 for i in range(len(tmp_slotted_aloha_i_list))];
        if len(slotted_aloha_c_list) == 0:
                slotted_aloha_c_list = [0 for i in range(len(tmp_slotted_aloha_c_list))];
        if len(csma_s_list) == 0:
            csma_s_list = [0 for i in range(len(tmp_csma_s_list))];
        if len(csma_i_list) == 0:
                csma_i_list = [0 for i in range(len(tmp_csma_i_list))];
        if len(csma_c_list) == 0:
                csma_c_list = [0 for i in range(len(tmp_csma_c_list))];
        if len(csma_cd_s_list) == 0:
            csma_cd_s_list = [0 for i in range(len(tmp_csma_cd_s_list))];
        if len(csma_cd_i_list) == 0:
                csma_cd_i_list = [0 for i in range(len(tmp_csma_cd_i_list))];
        if len(csma_cd_c_list) == 0:
                csma_cd_c_list = [0 for i in range(len(tmp_csma_cd_c_list))];
        aloha_s_list = [aloha_s_list[i] + tmp_aloha_s_list[i] for i in range(len(tmp_aloha_s_list))]
        aloha_i_list = [aloha_i_list[i] + tmp_aloha_i_list[i] for i in range(len(tmp_aloha_i_list))]
        aloha_c_list = [aloha_c_list[i] + tmp_aloha_c_list[i] for i in range(len(tmp_aloha_c_list))]
        slotted_aloha_s_list = [slotted_aloha_s_list[i] + tmp_slotted_aloha_s_list[i] for i in range(len(tmp_slotted_aloha_s_list))]
        slotted_aloha_i_list = [slotted_aloha_i_list[i] + tmp_slotted_aloha_i_list[i] for i in range(len(tmp_slotted_aloha_i_list))]
        slotted_aloha_c_list = [slotted_aloha_c_list[i] + tmp_slotted_aloha_c_list[i] for i in range(len(tmp_slotted_aloha_c_list))]
        csma_s_list = [csma_s_list[i] + tmp_csma_s_list[i] for i in range(len(tmp_csma_s_list))]
        csma_i_list = [csma_i_list[i] + tmp_csma_i_list[i] for i in range(len(tmp_csma_i_list))]
        csma_c_list = [csma_c_list[i] + tmp_csma_c_list[i] for i in range(len(tmp_csma_c_list))]
        csma_cd_s_list = [csma_cd_s_list[i] + tmp_csma_cd_s_list[i] for i in range(len(tmp_csma_cd_s_list))]
        csma_cd_i_list = [csma_cd_i_list[i] + tmp_csma_cd_i_list[i] for i in range(len(tmp_csma_cd_i_list))]
        csma_cd_c_list = [csma_cd_c_list[i] + tmp_csma_cd_c_list[i] for i in range(len(tmp_csma_cd_c_list))]
    # Plot the data
    aloha_s_list = [aloha_s_list[i]/test_times for i in range(len(aloha_s_list))]
    aloha_i_list = [aloha_i_list[i]/test_times for i in range(len(aloha_i_list))]
    aloha_c_list = [aloha_c_list[i]/test_times for i in range(len(aloha_c_list))]
    slotted_aloha_s_list = [slotted_aloha_s_list[i]/test_times for i in range(len(slotted_aloha_s_list))]
    slotted_aloha_i_list = [slotted_aloha_i_list[i]/test_times for i in range(len(slotted_aloha_i_list))]
    slotted_aloha_c_list = [slotted_aloha_c_list[i]/test_times for i in range(len(slotted_aloha_c_list))]
    csma_s_list = [csma_s_list[i]/test_times for i in range(len(csma_s_list))]
    csma_i_list = [csma_i_list[i]/test_times for i in range(len(csma_i_list))]
    csma_c_list = [csma_c_list[i]/test_times for i in range(len(csma_c_list))]
    csma_cd_s_list = [csma_cd_s_list[i]/test_times for i in range(len(csma_cd_s_list))]
    csma_cd_i_list = [csma_cd_i_list[i]/test_times for i in range(len(csma_cd_i_list))]
    csma_cd_c_list = [csma_cd_c_list[i]/test_times for i in range(len(csma_cd_c_list))]
    tick_locs = h_list
    tick_labels = [str(x) for x in h_list]
    plt.plot(h_list, aloha_s_list, label='ALOHA', marker='x', color='k')
    plt.plot(h_list, slotted_aloha_s_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(h_list, csma_s_list, label='CSMA', marker='^', color='g')
    plt.plot(h_list, csma_cd_s_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Host Num')
    plt.ylabel('Success Rate')
    plt.title("Influence of Host Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q6/success_rate_6.png")
    plt.cla()
    plt.clf()
    plt.plot(h_list, aloha_i_list, label='ALOHA', marker='x', color='k')
    plt.plot(h_list, slotted_aloha_i_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(h_list, csma_i_list, label='CSMA', marker='^', color='g')
    plt.plot(h_list, csma_cd_i_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Host Num')
    plt.ylabel('Idle Rate')
    plt.title("Influence of Host Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q6/idle_rate_6.png")
    plt.cla()
    plt.clf()
    plt.plot(h_list, aloha_c_list, label='ALOHA', marker='x', color='k')
    plt.plot(h_list, slotted_aloha_c_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(h_list, csma_c_list, label='CSMA', marker='^', color='g')
    plt.plot(h_list, csma_cd_c_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Host Num')
    plt.ylabel('Collision Rate')
    plt.title("Influence of Host Num")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q6/collision_rate_6.png")
    plt.cla()
    plt.clf()
    print('Q6 Done!')
    #!q7
    print('Processing Q7......')
    aloha_s_list.clear()
    slotted_aloha_s_list.clear()
    csma_s_list.clear()
    csma_cd_s_list.clear()
    aloha_i_list.clear()
    slotted_aloha_i_list.clear()
    csma_i_list.clear()
    csma_cd_i_list.clear()
    aloha_c_list.clear()
    slotted_aloha_c_list.clear()
    csma_c_list.clear()
    csma_cd_c_list.clear()
    ps_list = []
    for i in range(test_times):
        tmp_aloha_s_list = []
        tmp_aloha_i_list = []
        tmp_aloha_c_list = []
        tmp_slotted_aloha_s_list = []
        tmp_slotted_aloha_i_list = []
        tmp_slotted_aloha_c_list = []
        tmp_csma_s_list = []
        tmp_csma_cd_s_list = []
        tmp_csma_i_list = []
        tmp_csma_cd_i_list = []
        tmp_csma_c_list = []
        tmp_csma_cd_c_list = []
        for ps in range(1, 20, 1):
            setting = Setting(packet_size=ps)
            aloha_s, aloha_i, aloha_c = protocols.aloha(setting, False)
            slotted_aloha_s, slotted_aloha_i, slotted_aloha_c = protocols.slotted_aloha(setting, False)
            csma_s, csma_i, csma_c = protocols.csma(setting, False)
            csma_cd_s, csma_cd_i, csma_cd_c = protocols.csma_cd(setting, False)
            tmp_aloha_s_list.append(aloha_s)
            tmp_aloha_i_list.append(aloha_i)
            tmp_aloha_c_list.append(aloha_c)
            tmp_slotted_aloha_s_list.append(slotted_aloha_s)
            tmp_slotted_aloha_i_list.append(slotted_aloha_i)
            tmp_slotted_aloha_c_list.append(slotted_aloha_c)
            tmp_csma_s_list.append(csma_s)
            tmp_csma_cd_s_list.append(csma_cd_s)
            tmp_csma_i_list.append(csma_i)
            tmp_csma_cd_i_list.append(csma_cd_i)
            tmp_csma_c_list.append(csma_c)
            tmp_csma_cd_c_list.append(csma_cd_c)
            if i == 0:
                ps_list.append(ps)
            

        if len(aloha_s_list) == 0:
            aloha_s_list = [0 for i in range(len(tmp_aloha_s_list))];
        if len(aloha_i_list) == 0:
                aloha_i_list = [0 for i in range(len(tmp_aloha_i_list))];
        if len(aloha_c_list) == 0:
                aloha_c_list = [0 for i in range(len(tmp_aloha_c_list))];
        if len(slotted_aloha_s_list) == 0:
            slotted_aloha_s_list = [0 for i in range(len(tmp_slotted_aloha_s_list))];
        if len(slotted_aloha_i_list) == 0:
                slotted_aloha_i_list = [0 for i in range(len(tmp_slotted_aloha_i_list))];
        if len(slotted_aloha_c_list) == 0:
                slotted_aloha_c_list = [0 for i in range(len(tmp_slotted_aloha_c_list))];
        if len(csma_s_list) == 0:
            csma_s_list = [0 for i in range(len(tmp_csma_s_list))];
        if len(csma_i_list) == 0:
                csma_i_list = [0 for i in range(len(tmp_csma_i_list))];
        if len(csma_c_list) == 0:
                csma_c_list = [0 for i in range(len(tmp_csma_c_list))];
        if len(csma_cd_s_list) == 0:
            csma_cd_s_list = [0 for i in range(len(tmp_csma_cd_s_list))];
        if len(csma_cd_i_list) == 0:
                csma_cd_i_list = [0 for i in range(len(tmp_csma_cd_i_list))];
        if len(csma_cd_c_list) == 0:
                csma_cd_c_list = [0 for i in range(len(tmp_csma_cd_c_list))];
        aloha_s_list = [aloha_s_list[i] + tmp_aloha_s_list[i] for i in range(len(tmp_aloha_s_list))]
        aloha_i_list = [aloha_i_list[i] + tmp_aloha_i_list[i] for i in range(len(tmp_aloha_i_list))]
        aloha_c_list = [aloha_c_list[i] + tmp_aloha_c_list[i] for i in range(len(tmp_aloha_c_list))]
        slotted_aloha_s_list = [slotted_aloha_s_list[i] + tmp_slotted_aloha_s_list[i] for i in range(len(tmp_slotted_aloha_s_list))]
        slotted_aloha_i_list = [slotted_aloha_i_list[i] + tmp_slotted_aloha_i_list[i] for i in range(len(tmp_slotted_aloha_i_list))]
        slotted_aloha_c_list = [slotted_aloha_c_list[i] + tmp_slotted_aloha_c_list[i] for i in range(len(tmp_slotted_aloha_c_list))]
        csma_s_list = [csma_s_list[i] + tmp_csma_s_list[i] for i in range(len(tmp_csma_s_list))]
        csma_i_list = [csma_i_list[i] + tmp_csma_i_list[i] for i in range(len(tmp_csma_i_list))]
        csma_c_list = [csma_c_list[i] + tmp_csma_c_list[i] for i in range(len(tmp_csma_c_list))]
        csma_cd_s_list = [csma_cd_s_list[i] + tmp_csma_cd_s_list[i] for i in range(len(tmp_csma_cd_s_list))]
        csma_cd_i_list = [csma_cd_i_list[i] + tmp_csma_cd_i_list[i] for i in range(len(tmp_csma_cd_i_list))]
        csma_cd_c_list = [csma_cd_c_list[i] + tmp_csma_cd_c_list[i] for i in range(len(tmp_csma_cd_c_list))]
    # Plot the data
    aloha_s_list = [aloha_s_list[i]/test_times for i in range(len(aloha_s_list))]
    aloha_i_list = [aloha_i_list[i]/test_times for i in range(len(aloha_i_list))]
    aloha_c_list = [aloha_c_list[i]/test_times for i in range(len(aloha_c_list))]
    slotted_aloha_s_list = [slotted_aloha_s_list[i]/test_times for i in range(len(slotted_aloha_s_list))]
    slotted_aloha_i_list = [slotted_aloha_i_list[i]/test_times for i in range(len(slotted_aloha_i_list))]
    slotted_aloha_c_list = [slotted_aloha_c_list[i]/test_times for i in range(len(slotted_aloha_c_list))]
    csma_s_list = [csma_s_list[i]/test_times for i in range(len(csma_s_list))]
    csma_i_list = [csma_i_list[i]/test_times for i in range(len(csma_i_list))]
    csma_c_list = [csma_c_list[i]/test_times for i in range(len(csma_c_list))]
    csma_cd_s_list = [csma_cd_s_list[i]/test_times for i in range(len(csma_cd_s_list))]
    csma_cd_i_list = [csma_cd_i_list[i]/test_times for i in range(len(csma_cd_i_list))]
    csma_cd_c_list = [csma_cd_c_list[i]/test_times for i in range(len(csma_cd_c_list))]
    tick_locs = ps_list
    tick_labels = [str(x) for x in ps_list]
    plt.plot(ps_list, aloha_s_list, label='ALOHA', marker='x', color='k')
    plt.plot(ps_list, slotted_aloha_s_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(ps_list, csma_s_list, label='CSMA', marker='^', color='g')
    plt.plot(ps_list, csma_cd_s_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Packet Size')
    plt.ylabel('Success Rate')
    plt.title("Influence of Packet Size")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q7/success_rate_7.png")
    plt.cla()
    plt.clf()
    plt.plot(ps_list, aloha_i_list, label='ALOHA', marker='x', color='k')
    plt.plot(ps_list, slotted_aloha_i_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(ps_list, csma_i_list, label='CSMA', marker='^', color='g')
    plt.plot(ps_list, csma_cd_i_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Packet Size')
    plt.ylabel('Idle Rate')
    plt.title("Influence of Packet Size")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q7/idle_rate_7.png")
    plt.cla()
    plt.clf()
    plt.plot(ps_list, aloha_c_list, label='ALOHA', marker='x', color='k')
    plt.plot(ps_list, slotted_aloha_c_list, label='Slotted ALOHA', marker='s', color='r')
    plt.plot(ps_list, csma_c_list, label='CSMA', marker='^', color='g')
    plt.plot(ps_list, csma_cd_c_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Packet Size')
    plt.ylabel('Collision Rate')
    plt.title("Influence of Packet Size")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q7/collision_rate_7.png")
    plt.cla()
    plt.clf()
    print('Q7 Done!')
    #!q8
    print('Processing Q8......')
    csma_s_list.clear()
    csma_cd_s_list.clear()
    csma_i_list.clear()
    csma_cd_i_list.clear()
    csma_c_list.clear()
    csma_cd_c_list.clear()
    link_delay_list= [0,1,2,3]
    packet_size_list= [7,5,3,1]
    for i in range(test_times):
        tmp_csma_s_list = []
        tmp_csma_cd_s_list = []
        tmp_csma_i_list = []
        tmp_csma_cd_i_list = []
        tmp_csma_c_list = []
        tmp_csma_cd_c_list = []
        for l,p in zip(link_delay_list, packet_size_list):
            setting = Setting(link_delay=l, packet_size=p)
            # if l == 3:
            #     csma_s, csma_i, csma_c = protocols.csma(setting, True)
            # else:
            csma_s, csma_i, csma_c = protocols.csma(setting, False)
            # if l == 3:
            #     csma_cd_s, csma_cd_i, csma_cd_c = protocols.csma_cd(setting,True)
            # else:
            csma_cd_s, csma_cd_i, csma_cd_c = protocols.csma_cd(setting,False)
            tmp_csma_s_list.append(csma_s)
            tmp_csma_cd_s_list.append(csma_cd_s)
            tmp_csma_i_list.append(csma_i)
            tmp_csma_cd_i_list.append(csma_cd_i)
            tmp_csma_c_list.append(csma_c)
            tmp_csma_cd_c_list.append(csma_cd_c)
        if len(csma_s_list) == 0:
            csma_s_list = [0 for i in range(len(tmp_csma_s_list))];
        if len(csma_i_list) == 0:
                csma_i_list = [0 for i in range(len(tmp_csma_i_list))];
        if len(csma_c_list) == 0:
                csma_c_list = [0 for i in range(len(tmp_csma_c_list))];
        if len(csma_cd_s_list) == 0:
            csma_cd_s_list = [0 for i in range(len(tmp_csma_cd_s_list))];
        if len(csma_cd_i_list) == 0:
                csma_cd_i_list = [0 for i in range(len(tmp_csma_cd_i_list))];
        if len(csma_cd_c_list) == 0:
                csma_cd_c_list = [0 for i in range(len(tmp_csma_cd_c_list))];
        csma_s_list = [csma_s_list[i] + tmp_csma_s_list[i] for i in range(len(tmp_csma_s_list))]
        csma_i_list = [csma_i_list[i] + tmp_csma_i_list[i] for i in range(len(tmp_csma_i_list))]
        csma_c_list = [csma_c_list[i] + tmp_csma_c_list[i] for i in range(len(tmp_csma_c_list))]
        csma_cd_s_list = [csma_cd_s_list[i] + tmp_csma_cd_s_list[i] for i in range(len(tmp_csma_cd_s_list))]
        csma_cd_i_list = [csma_cd_i_list[i] + tmp_csma_cd_i_list[i] for i in range(len(tmp_csma_cd_i_list))]
        csma_cd_c_list = [csma_cd_c_list[i] + tmp_csma_cd_c_list[i] for i in range(len(tmp_csma_cd_c_list))]
    # Plot the data
    csma_s_list = [csma_s_list[i]/test_times for i in range(len(csma_s_list))]
    csma_i_list = [csma_i_list[i]/test_times for i in range(len(csma_i_list))]
    csma_c_list = [csma_c_list[i]/test_times for i in range(len(csma_c_list))]
    csma_cd_s_list = [csma_cd_s_list[i]/test_times for i in range(len(csma_cd_s_list))]
    csma_cd_i_list = [csma_cd_i_list[i]/test_times for i in range(len(csma_cd_i_list))]
    csma_cd_c_list = [csma_cd_c_list[i]/test_times for i in range(len(csma_cd_c_list))]
    tick_locs = link_delay_list
    tick_labels = [str(x) for x in link_delay_list]
    plt.plot(link_delay_list, csma_s_list, label='CSMA', marker='^', color='g')
    plt.plot(link_delay_list, csma_cd_s_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Link Delay')
    plt.ylabel('Success Rate')
    plt.title("Influence of Link Delay")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q8/success_rate_8.png")
    plt.cla()
    plt.clf()
    plt.plot(link_delay_list, csma_i_list, label='CSMA', marker='^', color='g')
    plt.plot(link_delay_list, csma_cd_i_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Link Delay')
    plt.ylabel('Idle Rate')
    plt.title("Influence of Link Delay")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q8/idle_rate_8.png")
    plt.cla()
    plt.clf()
    plt.plot(link_delay_list, csma_c_list, label='CSMA', marker='^', color='g')
    plt.plot(link_delay_list, csma_cd_c_list, label='CSMA/CD', marker='o', color='b')
    plt.xlabel('Link Delay')
    plt.ylabel('Collision Rate')
    plt.title("Influence of Link Delay")
    plt.legend()
    plt.xticks(tick_locs, tick_labels)
    plt.savefig("q8/collision_rate_8.png")
    plt.cla()
    plt.clf()
    print('Q8 Done!')

    
    
    

if __name__ == '__main__':
    main()
