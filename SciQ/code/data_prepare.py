import os
import numpy as np
import pickle
from generate_network_ready_files import generate_network_ready_files
import re

class prepare_data():
    def __init__(self,vec_path,processed_data_path,word_vec_size,max_q_length,max_option_length,max_opt_count,max_sent_para,max_words_sent):
        if not os.path.exists(processed_data_path):
            g_network_ready_files = generate_network_ready_files(vec_path,os.path.dirname(processed_data_path),word_vec_size,max_q_length,max_option_length,max_opt_count,max_sent_para,max_words_sent)
            g_network_ready_files.generate_word2vec_for_all()
        self.word_vec_size = word_vec_size
        self.num_of_words_in_opt = max_option_length
        self.num_of_words_in_question = max_q_length
        self.num_of_sents_in_closest_para = max_sent_para
        self.num_of_words_in_sent = max_words_sent
        self.num_of_options_for_quest = max_opt_count
        self.pad_word_vector = np.zeros((1, self.word_vec_size))
        self.pad_opt_vector = np.zeros((1, self.num_of_words_in_opt, self.word_vec_size))
        self.processed_data_path = processed_data_path
        self.folder_list = self.get_list_of_dirs(self.processed_data_path)
        self.options_file = ["a.pkl", "b.pkl", "c.pkl", "d.pkl"]
        self.correct_answer_file = "correct_answer.pkl"
        self.quest_file = "Question.pkl"
        self.sent_file = "support.pkl"

    def get_list_of_dirs(self,dir_path):
        dirlist = [name for name in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, name))]
        dirlist.sort()
        return dirlist

    def get_list_of_files(self,file_path,file_extension=".pkl"):
        filelist = []
        for root, dirs, files in os.walk(file_path):
            for filen in files:
                if filen.endswith(file_extension):
                    filelist.append(filen)
        filelist.sort()
        return filelist

    def read_options_files(self,question_dir_path):
        complete_array = None
        num_of_options = 0
        import re
        path = question_dir_path.replace("one_hot_files","text_question_sep_files")
        for f_name in self.options_file:
            # print(fname)
            if not os.path.exists(os.path.join(question_dir_path, f_name)):
                break
            
            g_name = f_name.replace("pkl","txt")
            #print path
            #print question_dir_path
            g = open(os.path.join(path,g_name),'r').read()
            # continue instead of break since forbidden option may not be the last option in sciq dataset
            if 'the above' in g:
                continue
            elif len(re.findall(r"^both [a-z] (and|&) [a-z]",g))>0:
                continue
            elif len(re.findall(r"^both \([a-z]\) (and|&) \([a-z]\)",g))>0:
                continue
            
            f = open(os.path.join(question_dir_path, f_name), 'r')
            complete_array_part = pickle.load(f)
            complete_array_part = complete_array_part.reshape(-1,self.word_vec_size)
            # print(" options : shape : " + str(complete_array_part.shape))
            if complete_array_part.shape[0] > self.num_of_words_in_opt:
                complete_array_part = complete_array_part[:self.num_of_words_in_opt,:]
            while complete_array_part.shape[0]<self.num_of_words_in_opt:
                complete_array_part = np.concatenate((complete_array_part, self.pad_word_vector), axis=0)
            # print(" options : shape : " + str(complete_array_part.shape))
            complete_array_part = complete_array_part.reshape(1,self.num_of_words_in_opt, self.word_vec_size)
            # print(" options : shape : " + str(complete_array_part.shape))
            complete_array = complete_array_part if complete_array is None else np.concatenate((complete_array, complete_array_part), axis=0)
            num_of_options+=1
        num_act_options = num_of_options
        while num_of_options<self.num_of_options_for_quest:
            complete_array = np.concatenate((complete_array, self.pad_opt_vector), axis=0)
            num_of_options+=1
        complete_array = complete_array.reshape(1,self.num_of_options_for_quest, self.num_of_words_in_opt, self.word_vec_size)
        # print(" options : shape : " + str(complete_array.shape))
        return complete_array,num_act_options

    def read_question_file(self,question_dir_path):
        f = open(os.path.join(question_dir_path, self.quest_file), 'r')
        complete_array = pickle.load(f)
        complete_array = complete_array.reshape(-1,self.word_vec_size)
        if complete_array.shape[0] > self.num_of_words_in_question:
            complete_array = complete_array[:self.num_of_words_in_question, :]
        while complete_array.shape[0] < self.num_of_words_in_question:
            complete_array = np.concatenate((complete_array, self.pad_word_vector), axis=0)
        complete_array = complete_array.reshape(1, self.num_of_words_in_question, self.word_vec_size)
        # print(" questions : shape : " + str(complete_array.shape))
        return complete_array

    def read_sentence_file(self,question_dir_path):
        f = open(os.path.join(question_dir_path, self.sent_file), 'r')
        complete_array = pickle.load(f)
        complete_array = np.expand_dims(complete_array,0)
        return complete_array

    def read_correct_ans_file(self,question_dir_path,num_act_options):
        # the last option is always the correct option in SciQ dataset so file correct_answer.pkl is not needed
        complete_array = np.zeros((1,4))
        # if a question has a forbidden option as incorrect option than correct answer will be at index num_act_options-1
        complete_array[:,num_act_options-1] = 1  
        return complete_array

    def get_forbidden_questions(self):
        # l has [folder,question_dir] to make it unique. question_dir is not unique.
        import re
        l = []
        path = self.processed_data_path.replace("one_hot_files","text_question_sep_files")
        for folder in self.folder_list:
            #print(folder)
            l_dir = os.path.join(path,folder)
            questions_dir = self.get_list_of_dirs(l_dir)
            for question_dir in questions_dir:
                #print(question_dir)
                ans = open(os.path.join(path,folder,question_dir,"correct_answer.txt"),"r").read()
                if 'the above' in ans:
                    l.append([folder,question_dir])
                elif len(re.findall(r"^both [a-z] (and|&) [a-z]",ans))>0:
                    l.append([folder,question_dir])
                elif len(re.findall(r"^both \([a-z]\) (and|&) \([a-z]\)",ans))>0:
                    l.append([folder,question_dir])
                doc = open(os.path.join(path,folder,question_dir,"support.txt"),"r").read()
                if doc == "" or doc == "\n":
                    l.append([folder,question_dir])
        return l

    def print_data_shape_details(self, data_name, x1, x2=None):
        if x2 is None:
            print(data_name + " : shape : " + str(x1.shape))
        else:
            print(data_name + " : train shape : " + str(x1.shape))
            print(data_name + " : test shape : " + str(x2.shape))


    def read_all_vectors(self):
        forbidden_list = self.get_forbidden_questions()
        print(len(forbidden_list))
        while(1):
            complete_options_mat = None
            complete_question_mat = None
            complete_sent_mat = None
            complete_correct_ans_mat = None

            number_of_folders = 0
            for folder in self.folder_list:
                l_dir = os.path.join(self.processed_data_path,folder)
                questions_dir = self.get_list_of_dirs(l_dir)
                questions_dir = [name for name in questions_dir if [folder,name] not in forbidden_list]
                for question_dir in questions_dir:
                    # file_list = self.get_list_of_files(os.path.join(l_dir,question_dir))
                    question_dir_path = os.path.join(l_dir,question_dir)
                    #print question_dir
                    #print ("Question : ", question_dir)
                    try:
                        options_mat,_ = self.read_options_files(question_dir_path)
                        question_mat = self.read_question_file(question_dir_path)
                        sent_mat = self.read_sentence_file(question_dir_path)
                        correct_ans_mat = self.read_correct_ans_file(question_dir_path,num_act_options=_)
                    except:
                        print(folder,question_dir)


                    complete_options_mat = options_mat if complete_options_mat is None else np.concatenate((complete_options_mat, options_mat), axis=0)
                    complete_question_mat = question_mat if complete_question_mat is None else np.concatenate((complete_question_mat, question_mat), axis=0)
                    complete_sent_mat = sent_mat if complete_sent_mat is None else np.concatenate((complete_sent_mat, sent_mat), axis=0)
                    complete_correct_ans_mat = correct_ans_mat if complete_correct_ans_mat is None else np.concatenate((complete_correct_ans_mat, correct_ans_mat), axis=0)
                number_of_folders+=1
            
                if number_of_folders>1:
                    if(complete_options_mat is not None):
                        yield [complete_question_mat, complete_sent_mat, complete_options_mat], complete_correct_ans_mat
                    complete_options_mat = None
                    complete_question_mat = None
                    complete_sent_mat = None
                    complete_correct_ans_mat = None
                    number_of_folders=0

