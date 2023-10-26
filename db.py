import sqlite3
import time
import numpy as np

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,)), \
                self.connection.commit()

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def set_password(self, user_id, password):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `password` = ? WHERE `user_id` = ?", (password, user_id,)), \
                self.connection.commit()

    def get_signup(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `signup` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                signup = str(row[0])
            return signup

    def set_signup(self, user_id, signup):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `signup` = ? WHERE `user_id` = ?", (signup, user_id,)), \
                self.connection.commit()

    def get_password(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                password = str(row[0])
            return password

    def set_time_sub(self, user_id, time_sub):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `time_sub` = ? WHERE `user_id` = ?", (time_sub, user_id,)), \
                self.connection.commit()

    def get_time_sub(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `time_sub` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                time_sub = int(row[0])
            return time_sub

    def get_sub_status(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT `time_sub` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            for row in result:
                time_sub = int(row[0])

            if time_sub > int(time.time()):
                return True
            else:
                return False

    def set_priority_flag(self, user_id):
        set_query = "UPDATE users SET priorityflag = 1 WHERE user_id = " + str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()

    def reset_priority_flag(self, user_id):
        set_query = "UPDATE users SET priorityflag = 0 WHERE user_id = " + str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()

    def get_priority_flag(self, user_id):
        with self.connection:
            output = self.cursor.execute("SELECT priorityflag from users where user_id = ?", (user_id,)).fetchall()
            if output is None:
                return 0
            else:
                return output[0][0]
            
    def get_priorities(self, user_id):
        with self.connection:
            output = self.cursor.execute("SELECT user_id, used, sleep, food, productivity, brain FROM users WHERE `user_id` = ?", (user_id,)).fetchall()
            user_id = output[0][0]
            used_list = output[0][1]
            priority_result = output[0][2:]
            return user_id, used_list, priority_result
        
        
    def daily_feature(self, user_id, used_list, sort_query):
        with self.connection:
            if used_list is None:
                used_list = ''
            query = "SELECT feature_id, feature, description, picture FROM phishki WHERE INSTR("+"'"+used_list+"'"+", ','||cast(feature_id as text)||',')=0 ORDER BY "+sort_query+" LIMIT 1"
            output = self.cursor.execute(query).fetchall()
            feature_id = output[0][0]
            feature = output[0][1]
            description = output[0][2]
            picture_url = output[0][3]
            return feature_id, feature, description, picture_url
    
    def user_used_update(self, user_id, feature_id, used_list):
        if used_list is None:
            used_list = ''
        new_used = used_list + ',' + str(feature_id) + ','
        update_query = "UPDATE users SET used = '"+new_used+"' WHERE user_id = "+str(user_id)
        with self.connection:
            return self.cursor.execute(update_query), \
                self.connection.commit()
    
    def set_priorities(self, user_id, priority):
        priorities = np.zeros(4)
        for i in priority:
            priorities[int(i)-1] = 1
        sleep, food, productivity, brain = priorities
        set_query = "UPDATE users SET sleep = "+str(sleep)+", food = "+str(food)+", productivity = "+str(productivity)+", brain = "+str(brain)+" WHERE user_id = "+str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()

    def reset_priorities(self, user_id):
        set_query = "UPDATE users SET sleep = 0, food = 0, productivity = 0, brain = 0 WHERE user_id = "+str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()

    def set_10(self, user_id):
        set_query = "UPDATE users SET tenflag = 1 WHERE user_id = "+str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()
            
    def reset_10(self, user_id):
        set_query = "UPDATE users SET tenflag = 0 WHERE user_id = "+str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()
    
    def get_10(self, user_id):
        with self.connection:
            output = self.cursor.execute("SELECT tenflag from users where user_id = ?", (user_id,)).fetchall()
            if output[0][0] is None:
                return 0
            else:
                return output[0][0]
    
    def get_features_count_current(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT feature_used FROM users WHERE user_id = ?", (user_id,)).fetchall()
            used = result[0][0]
            if used is None:
                used = ''
            return used.count(',')/2

    def get_features_used_current(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT feature_used FROM users WHERE user_id = ?", (user_id,)).fetchall()
            used = result[0][0]
            if used is None:
                used = ''
            return used

    def get_features_current(self, user_id, used):
        with self.connection:
            query = "SELECT feature FROM phishki WHERE INSTR("+"'"+used+"'"+", ','||cast(feature_id as text)||',')!=0 ORDER BY feature_id asc"
            output = self.cursor.execute(query).fetchall()
            feature_list = []
            for i in output:
                feature_list.append(i[0])
            return feature_list
    
    def feature_used_update(self, user_id, feature_id, feature_used_list):
        if feature_used_list is None:
            feature_used_list = ''
        new_used = feature_used_list + ',' + str(feature_id) + ','
        update_query = "UPDATE users SET feature_used = '" + new_used + "' WHERE user_id = " + str(user_id)
        with self.connection:
            return self.cursor.execute(update_query), \
                self.connection.commit()
    
    def reset_feature_current(self, user_id):
        set_query = "UPDATE users SET feature_used = '' WHERE user_id = "+str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()
    
    def set_21(self, user_id):
        set_query = "UPDATE users SET toflag = 1 WHERE user_id = "+str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()

    def reset_21(self, user_id):
        set_query = "UPDATE users SET toflag = 0 WHERE user_id = "+str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()

    def get_21(self, user_id):
        with self.connection:
            output = self.cursor.execute("SELECT toflag from users where user_id = ?", (user_id,)).fetchall()
            if output[0][0] is None:
                return 0
            else:
                return output[0][0]

    def get_days_count(self, user_id):
        with self.connection:
            output = self.cursor.execute("SELECT days_count from users where user_id = ?", (user_id,)).fetchall()
            if output[0][0] is None or output[0][0] == '':
                return 0
            else:
                return output[0][0]
    
    def plus_days_count(self, user_id, new_count):
        set_query = "UPDATE users SET days_count = "+str(new_count)+" WHERE user_id = "+str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()
    
    def reset_days_count(self, user_id):
        set_query = "UPDATE users SET days_count = 0 WHERE user_id = "+str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()

    def set_track(self, user_id, track_list):
        set_query = "UPDATE users SET track = ? WHERE user_id = ? "
        with self.connection:
            return self.cursor.execute("UPDATE users SET track = ? WHERE user_id = ? ", (track_list, user_id)), \
                self.connection.commit()
    
    def get_track(self, user_id):
        with self.connection:
            output = self.cursor.execute("SELECT track from users where user_id = ?", (user_id,)).fetchall()
            if output is None:
                return ''
            else:
                return output[0][0]

    def reset_track(self, user_id):
        set_query = "UPDATE users SET track = '' WHERE user_id = "+str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()

    def get_track_features(self, user_id, track):
        with self.connection:
            query = "SELECT feature FROM phishki WHERE INSTR("+"'"+track+"'"+", ','||cast(feature_id as text)||',')!=0 ORDER BY feature_id asc"
            output = self.cursor.execute(query).fetchall()
            feature_list = []
            for i in output:
                feature_list.append(i[0])
            return feature_list

    def get_ids(self):
        with self.connection:
            output = self.cursor.execute("SELECT user_id from users").fetchall()
            id_list = []
            for i in output:
                id_list.append(i[0])
            return id_list

    def set_track_flag(self, user_id):
        set_query = "UPDATE users SET trackflag = 1 WHERE user_id = " + str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()

    def reset_track_flag(self, user_id):
        set_query = "UPDATE users SET trackflag = 0 WHERE user_id = " + str(user_id)
        with self.connection:
            return self.cursor.execute(set_query), \
                self.connection.commit()

    def get_track_flag(self, user_id):
        with self.connection:
            output = self.cursor.execute("SELECT trackflag from users where user_id = ?", (user_id,)).fetchall()
            if output is None:
                return 0
            else:
                return output[0][0]


        
        

    
    

    
            
    
        
        
    def close(self):
        self.connection.close()
