from itertools import permutations

op_list = ["+", "-", "*", "/"]

def get_input():
    card_1 = int(input("first card point:\n"))
    card_2 = int(input("second card point:\n"))
    card_3 = int(input("third card point:\n"))
    card_4 = int(input("fourth card point:\n"))
    return [card_1, card_2, card_3, card_4]

'''
get_input()
'''

def is_24(val):
    if(abs(val-24)<0.000001):
        return 1
    else:
        return 0

def cal_one_step(a=1, b=1, op="+", order=1):
    if(op=="+"):
        return a+b
    elif(op=="*"):
        return a*b
    elif(op=="-"):
        if order:
            return a-b
        else:
            return b-a
    elif(op=="/"):
        if order:
            if b==0:
                return 1000000
            return a*1.0/b*1.0
        else:
            if a==0:
                return 1000000
            return b*1.0/a*1.0
    else:
        raise

def cal_two_all_op_result(a, b):
    all_result = []
    op_record = []
    for op in op_list:
        for order in [0,1]:
            all_result.append(cal_one_step(a,b,op,order))
            op_record.append([op, order])
    return all_result, op_record

'''
print(cal_two_all_op_result(1, 7))
'''

def reorder_card(card_list):
    all_com = []
    if(len(card_list) != 4):
        raise
    else:
        return list(permutations(card_list))
        
'''
card_list = get_input()
print(reorder_card(card_list))
print(len(reorder_card(card_list)))
'''

def cal_order_op_result(card_tp):
    '''
    第一种情况是1，2运算完之后的结果与3进行计算的结果，再与4计算
    第二种情况是1，2运算的结果与3，4运算的结果计算
    '''
    #case 1
    first_result, first_op = cal_two_all_op_result(card_tp[0], card_tp[1])
    
    #print(first_result)
    #print(first_op)
    
    second_result = []
    second_op = []
    for item in range(len(first_result)):
        tmp_result, tmp_op = cal_two_all_op_result(first_result[item], card_tp[2])
        second_result.extend(tmp_result)
    third_result = []
    third_op = []
    for item in second_result:
        tmp_result, tmp_op = cal_two_all_op_result(item, card_tp[3])
        third_result.extend(tmp_result)
    #print(third_result)
    #case 2
    first_result, first_op = cal_two_all_op_result(card_tp[0], card_tp[1])
    second_result, second_op = cal_two_all_op_result(card_tp[2], card_tp[3])
    for fitem in first_result:
        for sitem in second_result:
            tmp_result, third_op = cal_two_all_op_result(fitem, sitem)
            third_result.extend(tmp_result)
    #print(third_result)
    #print(len(third_result))
    op_index=[]
    for cnt in range(len(third_result)):
        if(is_24(third_result[cnt])):
            op_index.append(cnt)
    return op_index

def trans_op_cnt(op_cnt):
    return [op_list[op_cnt//2], op_cnt%2]

'''
for i in range(8):
    print(trans_op_cnt(i))
'''

def get_op_steps(op_cnt):
    op_case = op_cnt//512;
    op_cnt = op_cnt%512;
    step_num = [op_case, op_cnt//64, (op_cnt//8)%8, op_cnt%8]
    step_sig = []
    step_sig.append(step_num[0])
    for i in range(1,4):
        #print(trans_op_cnt(step_num[i]))
        step_sig.append(trans_op_cnt(step_num[i]))
    return step_num, step_sig


card_list = get_input()
all_result = []
#print(reorder_card(card_list))
#print(len(reorder_card(card_list)))
#card_inst = (4,5,8,2)
all_card_list = reorder_card(card_list)
#all_card_list = [(2,8,5,4)]
for card_inst in all_card_list:
    #print(card_inst)
    op_index_list = cal_order_op_result(card_inst)
    #print(op_index_list)
    if(len(op_index_list)>0):
        for item in op_index_list:
            cal_expr=""
            step_num, step_sig = get_op_steps(item)
            #print(step_num, step_sig)
            cal_expr = str(card_inst[0])
            if(step_sig[1][1]):
                cal_expr = "(" + cal_expr + step_sig[1][0] + \
                               str(card_inst[1]) + ")"
            else:
                cal_expr = "(" + str(card_inst[1]) + step_sig[1][0] + \
                                cal_expr + ")"                
            if(step_sig[0]==0):
                if(step_sig[2][1]):
                    cal_expr = "(" + cal_expr + step_sig[2][0] + \
                                   str(card_inst[2]) + ")"
                else:
                    cal_expr = "(" + str(card_inst[2]) + step_sig[2][0] + \
                                    cal_expr + ")"
                if(step_sig[3][1]):
                    cal_expr = "(" + cal_expr + step_sig[3][0] + \
                                   str(card_inst[3]) + ")"
                else:
                    cal_expr = "(" + str(card_inst[3]) + step_sig[3][0] + \
                                    cal_expr + ")"
            else:
                if(step_sig[2][1]):
                    cal_expr_tmp = "(" + str(card_inst[2]) + step_sig[2][0] + \
                                   str(card_inst[3]) + ")"
                else:
                    cal_expr_tmp = "(" + str(card_inst[3]) + step_sig[2][0] + \
                                   str(card_inst[2]) + ")"
                if(step_sig[3][1]):
                    cal_expr = "(" + cal_expr + step_sig[3][0] + \
                                   cal_expr_tmp + ")"
                else:
                    cal_expr = "(" + cal_expr_tmp + step_sig[3][0] + \
                                    cal_expr + ")"
            cal_expr = cal_expr + "=24"
            #print(step_sig[0])
            #print(cal_expr)
            all_result.append(cal_expr)

all_result_new = list(set(all_result))
if(len(all_result_new)>0):
    for item in all_result_new:
    #print(all_result_new)
        print(item)
else:
    print("I can not calculate to 24 point, can you tell me how to do it?")
            
            
        




                
        
    
    












        
        
