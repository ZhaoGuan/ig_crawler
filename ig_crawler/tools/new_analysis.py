#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import pymysql
import json
from tools.search_ig_persion import SearchIG
from tools.user_mysql import Statistics
from tools.googlesheet import GoogleSheet
import copy


class IGDB:
    def __init__(self):
        self.db = pymysql.connect("localhost", "root", "gz19891020", "ig", charset="utf8mb4")
        self.cursor = self.db.cursor()

    def insert_user(self, user_data):
        user_id = user_data["pk"]
        user_name = user_data["username"]
        full_name = pymysql.escape_string(user_data["full_name"])
        is_private = user_data["is_private"]
        is_business = user_data["is_business"]
        profile_pic_url = user_data["profile_pic_url"]
        hd_profile_pic_url_info = json.dumps(user_data["hd_profile_pic_url_info"])
        following_count = user_data["following_count"]
        follower_count = user_data["follower_count"]
        sql = """
        INSERT INTO user_data(user_id,user_name,full_name,is_private,is_business,profile_pic_url,hd_profile_pic_url_info,following_count,follower_count) 
        VALUES ('%s','%s',\'%s\',%s,%s,'%s','%s','%s','%s')
                 """ % (
            user_id, user_name, full_name, is_private, is_business, profile_pic_url, hd_profile_pic_url_info,
            following_count, follower_count)
        return sql

    def insert_following(self, master, following, following_username):
        sql = """
                INSERT INTO following(master_id,following,following_username) 
                VALUES ('%s','%s','%s')
                         """ % (master, following, following_username)
        return sql

    def insert_follower(self, master, follower, follower_username):
        sql = """
                INSERT INTO follower(master_id,follower,follower_username) 
                VALUES ('%s','%s','%s')
                         """ % (master, follower, follower_username)
        return sql

    def delete_master_following(self, master):
        sql = "DELETE FROM following WHERE master_id = %s" % (master)
        return sql

    def delete_master_follower(self, master):
        sql = "DELETE FROM follower WHERE master_id = %s" % (master)
        return sql

    def get_master_base_following(self, following):
        sql = "SELECT * FROM following WHERE fowllowing='%s'" % (following)
        return sql

    def get_following_base_master(self, master):
        sql = "SELECT * FROM following WHERE master_id='%s'" % (master)
        return sql

    def get_master_base_follower(self, follower):
        sql = "SELECT * FROM follower WHERE fowllower='%s'" % (follower)
        return sql

    def get_follower_base_master(self, master):
        sql = "SELECT * FROM follower WHERE master_id='%s'" % (master)
        return sql

    def get_user_base_user_name(self, user_name):
        sql = "SELECT * FROM user_data WHERE user_name='%s'" % (user_name)
        return sql

    def get_user_base_user_id(self, user_id):
        sql = "SELECT * FROM user_data WHERE user_id='%s'" % (user_id)
        return sql

    def get_username_from_following(self, user_id):
        sql = "SELECT following_username FROM `following` WHERE  `following`='%s'" % (
            user_id)
        return sql

    def get_username_from_follower(self, user_id):
        sql = "SELECT follower_username FROM `follower` WHERE  `follower`='%s'" % (
            user_id)
        return sql

    def run_insert_delete_sql(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
            return True
        except Exception as e:
            print(e)
            # print(sql)
            self.db.rollback()
            return False

    def run_select_sql(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        self.db.commit()
        return result


class UpdataIGDB:
    def __init__(self):
        self.igdb = IGDB()

    def insert_user(self, userdata):
        return self.igdb.run_insert_delete_sql(self.igdb.insert_user(userdata))

    def insert_user_following(self, master, following, following_username):
        self.igdb.run_insert_delete_sql(self.igdb.insert_following(master, following, following_username))

    def insert_user_follower(self, master, follower, follower_username):
        self.igdb.run_insert_delete_sql(self.igdb.insert_follower(master, follower, follower_username))

    def delete_user_following(self, master):
        self.igdb.run_insert_delete_sql(self.igdb.delete_master_following(master))

    def delete_user_follower(self, master):
        self.igdb.run_insert_delete_sql(self.igdb.delete_master_follower(master))

    def get_username_following(self, master):
        self.igdb.run_select_sql(self.igdb.get_username_from_following(master))

    def get_username_follower(self, master):
        self.igdb.run_select_sql(self.igdb.get_username_from_follower(master))


'''
向mysql插入数据
'''


def insert_all(json_file):
    ig = UpdataIGDB()
    count = 0
    with open(json_file) as f:
        for i in f:
            count += 1
            i = json.loads(i, encoding="utf-8")
            master = i["user_data"]["user"]["pk"]
            inster_user = ig.insert_user(i["user_data"]["user"])
            if inster_user:
                ig.delete_user_follower(master)
                ig.delete_user_following(master)
                for follower in i["follower"]:
                    ig.insert_user_follower(master, follower["pk"], follower["username"])
                for following in i["following"]:
                    ig.insert_user_following(master, following["pk"], following["username"])
    print(count)


class UserData:
    def __init__(self):
        self.ig = IGDB()
        self.up_ig = UpdataIGDB()
        self.is_research = False

    def user_data_base_username(self, username):
        user_data_result = {}
        result = self.ig.run_select_sql(self.ig.get_user_base_user_name(str(username)))
        if len(result) == 1:
            user_data = result[0]
            user_data_result['id'] = user_data[0]
            user_data_result['user_name'] = user_data[1]
            user_data_result['full_name'] = user_data[2]
            if user_data[3] == 0:
                user_data_result['is_private'] = False
            else:
                user_data_result['is_private'] = True
            if user_data[4] == 0:
                user_data_result['is_business'] = False
            else:
                user_data_result['is_business'] = True
            user_data_result['profile_pic_url'] = user_data[5]
            user_data_result['hd_profile_pic_url_info'] = json.loads(user_data[6])
            user_data_result["following_count"] = user_data[7]
            user_data_result["follower_count"] = user_data[8]
            return user_data_result
        else:
            if self.is_research:
                return self.user_data_base_username_research(username)
            else:
                return False

    def user_data_base_username_research(self, username):
        user_data = self.s_ig.user_data(username)
        if user_data is False:
            return False
        master = user_data["user_data"]["user"]["pk"]
        insert_user = self.up_ig.insert_user(user_data["user_data"]["user"])
        if insert_user:
            self.up_ig.delete_user_follower(master)
            self.up_ig.delete_user_following(master)
            if user_data["follower"]:
                for follower in user_data["follower"]:
                    self.up_ig.insert_user_follower(master, follower["pk"], follower["username"])
            if user_data["following"]:
                for following in user_data["following"]:
                    self.up_ig.insert_user_following(master, following["pk"], following["username"])
            return self.user_data_base_username(username)
        else:
            return False

    def user_data_base_user_id(self, user_id):
        user_data_result = {}
        result = self.ig.run_select_sql(self.ig.get_user_base_user_id(str(user_id)))
        if len(result) == 1:
            user_data = result[0]
            user_data_result['id'] = user_data[0]
            user_data_result['user_name'] = user_data[1]
            user_data_result['full_name'] = user_data[2]
            if user_data[3] == 0:
                user_data_result['is_private'] = False
            else:
                user_data_result['is_private'] = True
            if user_data[4] == 0:
                user_data_result['is_business'] = False
            else:
                user_data_result['is_business'] = True
            user_data_result['profile_pic_url'] = user_data[5]
            user_data_result['hd_profile_pic_url_info'] = json.loads(user_data[6])
            user_data_result["following_count"] = user_data[7]
            user_data_result["follower_count"] = user_data[8]
            return user_data_result
        else:
            if self.is_research:
                return self.user_data_base_user_id_research(user_id)
            else:
                return False

    def user_data_base_user_id_research(self, user_id):
        user_name = self.get_username_from_following_or_follower(user_id)
        if user_name:
            user_data = self.s_ig.user_data(user_name)
            if user_data is False:
                return False
            master = user_data["user_data"]["user"]["pk"]
            inster_user = self.up_ig.insert_user(user_data["user_data"]["user"])
            if inster_user:
                self.up_ig.delete_user_follower(master)
                self.up_ig.delete_user_following(master)
                if user_data["follower"]:
                    for follower in user_data["follower"]:
                        self.up_ig.insert_user_follower(master, follower["pk"], follower["username"])
                if user_data["following"]:
                    for following in user_data["following"]:
                        self.up_ig.insert_user_following(master, following["pk"], following["username"])
                return self.user_data_base_username(user_id)
            else:
                return False
        else:
            return False

    def following(self, master_id):
        result = self.ig.run_select_sql(self.ig.get_following_base_master(str(master_id)))
        if result:
            i_following = [{"id": i[1], "name": i[2]} for i in result]
            return i_following
        else:
            return False

    def follower(self, master_id):
        result = self.ig.run_select_sql(self.ig.get_follower_base_master(str(master_id)))
        if result:
            i_follower = [{"id": i[1], "name": i[2]} for i in result]
            return i_follower
        else:
            return False

    def friends(self, master_id):
        following = self.following(master_id)
        follower = self.follower(master_id)
        if follower is False or following is False:
            return False
        id_list = []
        user_mapping = {}
        for i in following:
            t_id = i["id"]
            t_name = i["name"]
            if t_id not in id_list:
                user_mapping[t_id] = t_name
        for i in follower:
            t_id = i["id"]
            t_name = i["name"]
            if t_id not in id_list:
                user_mapping[t_id] = t_name
        following_id = [i["id"] for i in following]
        follower_id = [i["id"] for i in follower]
        friends = set(following_id).intersection(set(follower_id))
        friends = [{"id": i, "name": user_mapping[i]} for i in friends]
        return friends

    def t_friends(self, master_id):
        following = self.following(master_id)
        follower = self.follower(master_id)
        if follower is False or following is False:
            return False
        id_list = []
        user_mapping = {}
        for i in following:
            t_id = i["id"]
            t_name = i["name"]
            if t_id not in id_list:
                user_mapping[t_id] = t_name
        for i in follower:
            t_id = i["id"]
            t_name = i["name"]
            if t_id not in id_list:
                user_mapping[t_id] = t_name
        following_id = [i["id"] for i in following]
        follower_id = [i["id"] for i in follower]
        friends = []
        for i in following_id:
            if i not in friends and i in follower_id:
                friends.append(i)
        friends = [{"id": i, "name": user_mapping[i]} for i in friends]
        return friends

    def get_username_following(self, following):
        result = self.ig.run_select_sql(self.ig.get_username_from_following(following))
        if len(result) > 0:
            return result[0][0]
        else:
            return False

    def get_username_follower(self, follower):
        result = self.ig.run_select_sql(self.ig.get_username_from_following(follower))
        if len(result) > 0:
            return result[0][0]
        else:
            return False

    def get_username_from_following_or_follower(self, user_id):
        following_result = self.get_username_following(user_id)
        follower_result = self.get_username_follower(user_id)
        if follower_result or follower_result:
            if follower_result:
                return follower_result
            else:
                return following_result
        else:
            return False


"""抄的"""


def mapping_sort_from_list(data: list):
    value = set(data)
    times = []
    index = []
    for i in value:
        times.append(data.count(i))
        index.append(data.index(i))
    res = []
    for i in zip(value, times, index):
        res.append(i)
    res = sorted(res, key=lambda x: (-x[1], x[2]))  # 负号表示从大到小，因为默认是从小到大
    ans = []
    for item in res:
        ans += [item[0]] * item[1]
    result = {}
    for i in ans:
        if i not in result:
            result[i] = 1
        else:
            result[i] += 1
    return result


def intersection(r, m):
    result = list(set(r).intersection(set(m)))
    return result


def union(r, m):
    return list(set(r).union(set(m)))


def sort_by_value(d):
    items = d.items()
    backitems = [[v[1], v[0]] for v in items]
    backitems.sort(reverse=True)
    return [backitems[i][1] for i in range(0, len(backitems))]


class Analysis:
    def __init__(self):
        self.igdb = IGDB()
        self.ud = UserData()

    def my_all(self, name):
        user_data = self.ud.user_data_base_username(name)
        id = user_data["id"]
        followings = self.ud.following(id)
        following_id = [f["id"] for f in followings]
        followers = self.ud.follower(id)
        follower_id = [f["id"] for f in followers]
        friends = self.ud.friends(id)
        friends_id = [f["id"] for f in friends]
        all_user = union(follower_id, following_id)
        all_data = {}
        result = {}
        for user in all_user:
            t_follower = self.ud.follower(user)
            if t_follower is False:
                continue
            t_follower = [f["id"] for f in t_follower]
            t_following = self.ud.following(user)
            if t_following is False:
                continue
            t_following = [f["id"] for f in t_following]
            t_friend = [f["id"] for f in self.ud.friends(user)]
            all_data[user] = {'follower': t_follower, "following": t_following, "friends": t_friend}
        for id, data in all_data.items():
            follower_follower = intersection(follower_id, data["follower"])
            follower_follower = len(follower_follower)
            following_follower = intersection(following_id, data["follower"])
            following_follower = len(following_follower)
            follower_following = intersection(follower_id, data["following"])
            follower_following = len(follower_following)
            following_following = intersection(following_id, data["following"])
            following_following = len(following_following)
            friends_friends = intersection(friends_id, data["friends"])
            friends_friends = len(friends_friends)
            data = self.ud.user_data_base_user_id(id)
            name = data["user_name"]
            full_name = data["full_name"]
            data = {"name": name, "full_name": full_name, "follower_follower": follower_follower,
                    "following_follower": following_follower,
                    "following_following": following_following, "follower_following": follower_following,
                    "friends_friends": friends_friends}
            result[id] = data
        return result

    def friends_group(self, name):
        user_data = self.ud.user_data_base_username(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        all_user = friends_id
        all_data = {my_id: friends_id}
        intersection_data = {}
        for user in all_user:
            t_friend = self.ud.friends(user)
            if t_friend is False:
                continue
            t_friend = [f["id"] for f in t_friend]
            try:
                t_friend.remove(my_id)
            except:
                pass
            all_data[user] = t_friend
        for id, data in all_data.items():
            data = intersection(friends_id, data)
            if len(data) == 0:
                continue
            intersection_data[id] = data
        print(all_data)
        print(intersection_data)
        # all_data = {
        #     # '4140774272': ['254638430', '42502137', '3037318828', '4009415770', '682270', '266913770', '228160939',
        #     #                '17625021', '2049692', '38569514', '3598953314', '41069358', '2069628', '3537056619',
        #     #                '1916698080', '1473858700', '529914741', '1339999012', '5780272989', '34810713',
        #     #                '5625418090',
        #     #                '2293895854', '7582174347', '2305618880', '5573484158', '1186210811', '2134439879',
        #     #                '33961614',
        #     #                '3906768725', '270339026', '804837047', '1474272023', '29720685', '54650679', '5606253289',
        #     #                '530984452', '1598311938', '1044590017', '3040634', '8935718315', '821792', '144166',
        #     #                '1982324715', '5973413688', '273481', '1467477592', '2947007029', '14837682', '29109254',
        #     #                '181603649', '10239933', '6862672481', '4790080914', '1666189105', '11632197068', '14497357',
        #     #                '223257503', '17297519', '375451348', '26001306', '25937844225'],
        #     '254638430': ['25428513', '328968385', '277579253', '236973292', '3307586796', '7955852246', '4111464505',
        #                   '1444587269', '183092235', '419407963', '21212061', '143748393', '249121829', '2251903244',
        #                   '2071864259', '623986055', '54758146', '8678600020', '6741160311', '25993169', '341766522',
        #                   '2247284586', '38020789', '201413171', '271259104', '224478749', '520115501', '502525254',
        #                   '3433698656', '3964435407', '6835674044', '393053988', '813492115', '386578517', '1401579081',
        #                   '219784466', '460595413', '414527087', '5368146163', '209830595', '44388781', '1463101230',
        #                   '257349747', '272825994', '8075331257', '12769675', '270313854', '144166', '306706016',
        #                   '145818990', '2278193997', '48412474', '3440743055', '4992213217', '3003140842', '4343621086',
        #                   '1460369042', '3126933907', '258313408', '226502934', '302684451', '502608354', '3112003535',
        #                   '226963750', '409125161', '298820200', '4598800', '350264903', '251039322', '3030345344',
        #                   '321894949', '2243766084', '976423076', '230845194', '560260964', '3537056619', '7570135149',
        #                   '357365027', '5172501', '27389612', '236296074', '46012811', '30406', '213413196',
        #                   '4655461001',
        #                   '35535309', '261170641', '3498946543', '332754904', '216952784', '279706973', '306141559',
        #                   '1458833470', '407188133', '705703723', '8471109444', '225627453', '659471291', '1111916142',
        #                   '335350694', '46449947', '1950929951', '331672860', '360419829', '611342889', '1597928624',
        #                   '1362856195', '265968109', '49784004', '1679215855', '212242340', '340739502', '385626079',
        #                   '3927527575', '251147790', '364779536', '145713768', '3653980192', '230284869', '272288747',
        #                   '370678436', '334246763', '2239968233', '46077845', '1465190793', '232474806', '42087455',
        #                   '509138672', '2073605812', '421698666', '179314074', '215740255', '287878425', '477306200',
        #                   '199226144', '9482995', '1385877798', '17625021', '6971218472', '55331732', '16998426',
        #                   '1577691514', '4140774272', '229185230', '178857399', '19843721', '311213172', '686275812',
        #                   '5625418090', '8561472391', '7826134', '192289415', '1664640516', '313161088', '468875990',
        #                   '6175942683', '1639654192', '558885172', '473861553', '204941079', '1928805743', '3242259933',
        #                   '277113432', '252336956', '236012984', '1721394015', '1237529812', '193609496', '3454827902',
        #                   '203848986', '261832882', '1555946305', '173690089', '1391817102', '180909770', '3775988',
        #                   '1496159926', '40459712', '26661492', '1087942460', '6770037', '31178070', '386881217',
        #                   '1354479395', '294368969', '7309745175', '7298714862', '1219993597', '4790080914',
        #                   '219741424',
        #                   '4143651428', '404781164', '251806471', '30307682', '262867539', '375451348', '49239487',
        #                   '226806422', '1361014474', '10618948577', '17647274', '1757826455', '463466392', '969177373',
        #                   '1133859758', '270821632', '4265856534', '3730923014', '308571900', '1005728167',
        #                   '8502059062',
        #                   '648768209', '353168791', '627247388', '8149663261', '45638129', '1206893185', '304154043',
        #                   '198879639', '3044960369', '49395660', '285049919', '750572126', '225767895', '363917134',
        #                   '448368234', '243809100', '332685312', '1144892574', '225325979', '3573238266', '2155048072',
        #                   '619575192', '1466763615', '900958417', '1134064201', '269392831', '21636661097', '231677423',
        #                   '1724245792', '14027047', '48161496', '3264461860', '2045845377', '487369669', '324647759',
        #                   '310444267', '370841492', '1362783147', '742163934', '420389777', '434883798', '683461926',
        #                   '410514859', '10434592877', '211117922', '810967406', '434740429', '1291591059', '3999987117',
        #                   '1052560644', '999196287', '3283064530', '840093123', '3317069961', '542890123'],
        #     '42502137': ['42323124', '10814562', '31832622', '37015818', '605058810', '3994373816', '3536013027',
        #                  '3864573354', '6371868748', '39267895', '7083942864', '4140774272', '371717065', '6251652152',
        #                  '2253914110', '4585438643', '1450105125', '1557076843', '4482027156', '8316982581',
        #                  '2545557214',
        #                  '3231700887', '290987616', '54650679', '7338656059', '552967255', '3669263296', '332979775',
        #                  '5472396180', '1613532', '422890645', '273481', '1976594220', '278979731', '1384017174',
        #                  '181603649', '6344378730', '37324060', '37243812', '597435', '382347386', '293641638',
        #                  '144141501', '1331894594'],
        #     '3037318828': ['195903207', '204053', '3642001745', '186743327', '293129166', '23744', '254945447',
        #                    '1276778573', '1409911588', '5351329590', '5489038465', '4140774272', '2055009417',
        #                    '2063683003', '651311165', '4023954057', '579584064', '1276110055', '1296282831',
        #                    '1818557017',
        #                    '1988891161', '11981937', '2236631652', '228453441', '683673', '2875697637', '1510687092',
        #                    '1198670985', '349500', '8177057', '186817484', '3021147067', '4283284342', '329459985',
        #                    '7212888', '1136099094', '267810464', '826298', '4870155807', '1174679863', '1474272023',
        #                    '456877481'],
        #     '4009415770': ['4281892', '23862106', '2080826', '36730212', '3642001745', '10814562', '770095', '3968453',
        #                    '3887959', '200452762', '1743098940', '1543985035', '1306765267', '38307106', '4560190894',
        #                    '529914741', '4140774272', '28243753', '371717065', '7066814', '4349150235', '3286187494',
        #                    '2025500', '337716727', '385813', '877670', '9863390', '23090020', '910688', '2392409',
        #                    '683673', '1655023840', '1195824', '1474272023', '3040634', '349500', '8177057', '191682472',
        #                    '1237131556', '36617792', '273481', '35850787', '181603649', '760434507', '3533039091',
        #                    '7212888', '267810464', '6143158169', '3775929113', '28786284', '1149511346', '26001306',
        #                    '317296357', '334119527'],
        #     '682270': ['36730212', '10814562', '266913770', '3968453', '53198861', '2049692', '2069628', '3537056619',
        #                '345194903', '3569118258', '4140774272', '360504484', '287226161', '371717065', '3839116196',
        #                '318152963', '520895447', '43622454', '3617203316', '357634', '5846156889', '6698646055',
        #                '2134439879', '37023964', '3164014609', '1045222600', '33104959', '2954056694', '47586672',
        #                '5572997372', '1420944193', '1493685744', '337385624', '15666662', '1467477592', '1481164721',
        #                '1613532', '36889302', '4183694561', '1120298145', '1360348', '1359643', '1426868352',
        #                '19088925',
        #                '246415083'],
        #     '266913770': ['913601103', '4124986319', '2049692', '2069628', '925118259', '9842179930', '385813',
        #                   '41266842',
        #                   '2253914110', '3401328667', '367808457', '9275868339', '1225942738', '604297175', '517318742',
        #                   '6625350624', '270200632', '37243812', '175319255', '568865232'],
        #     '228160939': ['35430556', '18343618', '14615595', '2474376851', '32340412', '8149663261', '32379475',
        #                   '4140774272', '7384631603', '1486964518', '252332554', '319022252', '11806415', '5371640541',
        #                   '2028505559', '664620', '4670438', '3580628490', '44035913', '7185862661', '1998049145',
        #                   '430324136', '241410560', '523141679', '23652492', '37466681', '316824009', '466827114',
        #                   '7871047', '306431789', '776183829', '3247306', '3448869214', '17297519', '3112003535',
        #                   '1507859612', '375451348', '4268664', '302386150'],
        #     '2049692': ['1775455348', '36730212', '682270', '266913770', '4765226894', '1771818', '37015818', '2069628',
        #                 '25876561', '4140774272', '14665229', '371717065', '28340731', '11578062', '190018243',
        #                 '9610438064', '334379685', '5311512', '754150009', '2253914110', '5600826432', '3429839',
        #                 '1271320047', '1474272023', '1943806', '47586672', '49100443', '22823963', '31725418', '821792',
        #                 '3029403321', '273481', '1467477592', '223496725', '1112321164', '2178788', '2056568',
        #                 '38330973',
        #                 '10843156', '4434484804', '26001306'],
        #     '38569514': ['427206114', '19418980', '1437100295', '8199485110', '1279730', '2025497', '4606115898',
        #                  '5123970', '5715213821', '2282953', '4158694814', '325364427', '1496763', '1381067747',
        #                  '23090020', '6219019630', '7786087380', '3614360294', '39807758', '3928120091', '387369',
        #                  '3362282', '7496008931', '4352747729', '477098566', '1713121275', '5689823980', '47621637',
        #                  '22007857', '2535494420', '134234', '186077517', '402480555', '26954426', '1653124598',
        #                  '200399',
        #                  '28228405', '4331255127', '13388381795', '4570390955', '2885288', '3993578', '1604846534',
        #                  '8640140547', '3525246721', '861283463', '6676658296', '967254', '755946', '109809', '450494',
        #                  '8204642148', '15030285', '680758428', '821004850', '676018475', '2814447378', '1637235',
        #                  '17571552', '699811333', '171141', '417083857', '4119255', '2487827', '1701501', '19593762',
        #                  '1188088141', '6148460', '4537789761', '126377', '13277618290', '8181100', '1758778',
        #                  '1937167',
        #                  '311082526', '275816681', '32868523', '5554173642', '35315808', '43371461', '8397524011',
        #                  '4140774272', '2111003407', '5314303872', '4965030037', '1280675338', '8675275582', '12621320',
        #                  '1649549859', '25534710368', '665636', '9005061186', '33064594', '189739472', '181562647',
        #                  '6728053998', '13309012', '1061991', '5883254673', '14837682', '145721', '51130848',
        #                  '7229774701',
        #                  '1126004', '5658269116', '2102953304', '8977588794', '8573573882', '9016540286', '33907674',
        #                  '317143', '4862108', '1346144', '4068442465', '8319229776', '36695455', '8984980717',
        #                  '2025500',
        #                  '13112746281', '19699179', '187726653', '45272313', '2896009', '1675880', '440604519',
        #                  '190351',
        #                  '3117098670', '5945324717', '5922897670', '5929175283', '31454952', '5451355913', '3268450959',
        #                  '202569961', '4166693008', '201280', '35943811', '4561361314'],
        #     '2069628': ['22913914', '821792', '745288', '36730212', '2178788', '682270', '1012576031', '266913770',
        #                 '683673', '1474272023', '4765226894', '2049692', '2253914110', '26001306', '32195100',
        #                 '4140774272'],
        #     '3537056619': ['254638430', '682270', '45638129', '458093580', '27068822', '1481798245', '4140774272',
        #                    '5625418090', '4351095604', '4179416713', '4121116504', '2206406185', '1716473606',
        #                    '5569188486', '1450119545', '48412474', '4790080914', '507438555', '4370676432', '211527197',
        #                    '217358105', '3193256577', '3112003535', '20374163'],
        #     '529914741': ['8516130', '10814562', '4009415770', '770095', '1087842', '3968453', '236568', '461921313',
        #                   '4140774272', '590822115', '605094194', '4046224464', '3960530', '8469296250', '1695182331',
        #                   '29720685', '40890912', '821792', '865731515', '51130848', '14837682', '221292', '6209796941',
        #                   '2982843403', '9333070', '4584803473'],
        #     '5780272989': ['5803844408', '5538299022', '270339026', '1182840770', '4140774272'],
        #     '5625418090': ['254638430', '331821711', '3598953314', '3537056619', '1570636738', '4140774272',
        #                    '3734749188',
        #                    '6131765230', '2247284586', '5837854733', '6202209524', '2305618880', '274485444',
        #                    '44658653',
        #                    '1224223822', '4021343222', '3054256207', '1124264713', '5339898287', '1044590017',
        #                    '6932942726', '53236174', '410514859', '4238616452', '1572970849', '1666189105',
        #                    '5571543672',
        #                    '3112003535', '357693677'],
        #     '2293895854': ['209843449', '1512682299', '13405321', '33961614', '2025500', '2293870171', '3242210872',
        #                    '4140774272'], '7582174347': ['4265312191', '3676061068', '4140774272'],
        #     '2305618880': ['4299914666', '37162186', '1664883', '1206893185', '4140774272', '3734749188', '1806638935',
        #                    '3511568', '5625418090', '1144892574', '2247284586', '5837854733', '3537000279', '55568335',
        #                    '104830957', '19439977', '48066069', '3054256207', '5884237349', '180909770', '1293940469',
        #                    '144166', '2294570301', '1679215855', '410514859', '1666189105', '5606732930', '4774032475',
        #                    '3415573749', '3610986148'],
        #     '5573484158': ['612362804', '687168033', '526772710', '226665622', '31395992', '1390751486', '308391519',
        #                    '443688996', '8753258296', '1405020933', '43060026', '221687281', '517079645', '306991587',
        #                    '288446256', '235944091', '5097244815', '4140774272', '478513712', '2315642860', '634037314',
        #                    '253846373', '1222983569', '2675580', '44528674', '5368930116', '4052052195', '285408724',
        #                    '23141444', '7129883599', '50317399', '214241331', '1594293904', '1528822504', '199467782',
        #                    '628378943', '218362495', '253499117', '290815308', '1720237424', '55029735', '805565451',
        #                    '2364523871', '3655708546', '1986490256', '1717290544', '608177367', '409668705',
        #                    '664053646',
        #                    '1009899576', '200370062', '4935823300', '8160842567', '8023619409', '223778264',
        #                    '2226763046',
        #                    '38071253', '491704653', '26630725', '1911760038', '449992308', '9278754161', '2187294',
        #                    '4140046414'],
        #     '1186210811': ['23862106', '2869126', '176408', '2048904', '10814562', '1451156', '1560626', '492383911',
        #                    '53198861', '4140774272', '1345919', '7804332', '7066814', '651311165', '910688',
        #                    '201838919',
        #                    '522936351', '54650679', '22823963', '273481', '29109254', '37324060', '37243812',
        #                    '10843156',
        #                    '597435'],
        #     '2134439879': ['3272662096', '327919292', '4204131921', '5597608232', '682270', '4334490575', '10522827',
        #                    '50838997', '3234482606', '4140774272', '3589749336', '1605181425', '3192880608',
        #                    '3550089641',
        #                    '1723433446', '18295488941', '1723146180', '1804844393', '6160171115', '4334050900',
        #                    '475704696'],
        #     '33961614': ['7956064726', '9474800', '232638168', '26670477', '2075507035', '14452790', '5527672749',
        #                  '1004897257', '2282833484', '8631266654', '4134007185', '5684061616', '1132752377',
        #                  '4140774272',
        #                  '37044357', '40524758', '7066806898', '699279424', '7456333737', '35174174', '4224354582',
        #                  '1690110', '6251652152', '8905725322', '235235611', '1513382676', '5315784458', '9952090',
        #                  '41555851', '1558922510', '363368956', '4933476848', '45089417', '857504', '1063813019',
        #                  '5606253289', '18411032', '8608056612', '1094922768', '5862818432', '7403953255', '2120586995',
        #                  '821792', '3555235038', '624827558', '1613532', '1761318029', '3626544152', '193845803',
        #                  '14837682', '5477966810', '295145475', '31816156', '480435020', '2123842781', '2057301277',
        #                  '505414063', '1463275259'],
        #     '1474272023': ['3037318828', '53198861', '2069628', '913542998', '5607300703', '789715', '1950946',
        #                    '2253914110', '1202936894', '1084807', '244095533', '1259416070', '902894', '226878586',
        #                    '3454946035', '26001306', '22913914', '1832796360', '2207055966', '4009415770', '181304519',
        #                    '954964', '15652097', '7690147785', '3586492222', '31243229', '1175849753', '227547516',
        #                    '5931858600', '29720685', '47586672', '287619373', '8493233', '22823963', '368293335',
        #                    '745288',
        #                    '1522113407', '1930846376', '181603649', '653466302', '37243812', '10843156', '327459833',
        #                    '7356777556', '23862106', '10814562', '1451156', '266913770', '1560626', '2049692',
        #                    '4158914349', '8991341233', '4140774272', '1537346947', '1450105125', '41669671',
        #                    '5761696493',
        #                    '54650679', '7338656059', '349500', '821792', '4713800484', '273481', '1467477592',
        #                    '229806824',
        #                    '37324060', '4401932064', '843144424', '223257503', '215537718', '1576843', '2231702326',
        #                    '4122320092', '1390286659', '1292021077', '7066814', '292636475', '1196820560', '6295498643',
        #                    '1552569137', '2070887075', '1382820502', '537895060', '17103723', '5638954011', '471777823',
        #                    '199703939', '3546501', '269828', '6991921311', '4567561493', '1500008331', '28422793',
        #                    '5782154372', '3681170', '3685751704', '270828', '20566592'],
        #     '29720685': ['272031', '1512682299', '821792', '2326905956', '14837682', '439625929', '1474272023',
        #                  '529914741', '7912300853', '16210755', '306016578', '461921313', '4140774272'],
        #     '54650679': ['4082346266', '184746052', '1724290459', '43461583', '9151298', '3968453', '301451411',
        #                  '53198861', '30779274', '386746657', '3960530', '38518198', '33256033', '1186210811',
        #                  '7435866258', '1313227', '1528545', '24949920', '1366471657', '194570125', '312960789',
        #                  '14705133', '256049052', '543461606', '971709367', '463336775', '144141501', '5636837515',
        #                  '299626896', '42502137', '217218', '176865276', '3306694945', '1468620485', '5438379',
        #                  '16699572',
        #                  '30601199', '48202776', '479726717', '3062292968', '1211554078', '6251652152', '1695182331',
        #                  '190569254', '4173415807', '201333092', '821004850', '34752572', '191447039', '552967255',
        #                  '1448437728', '8651723035', '19878378', '254937510', '36889302', '181603649', '190839039',
        #                  '236482771', '37243812', '1474272023', '29825214', '1504791046', '2936562', '4140774272',
        #                  '23883300', '4920578959', '307289816', '1421977538', '144301608', '239210230', '6898277753',
        #                  '690240690', '2664633439', '7691496486', '25038132766', '273481', '409103857', '1131988086',
        #                  '648014892', '1993337833', '6975683337', '266822800', '1045500522', '305419221', '1512814864',
        #                  '2345209', '555174', '26685926', '7009223485', '683673', '5737836879', '23597045', '190351',
        #                  '392334404', '6666264346', '3853254792', '865731515', '3821808685', '1432198230', '54184774',
        #                  '23382377', '597435'], '5606253289': ['1512682299', '33961614', '4140774272'],
        #     '1044590017': ['740472174', '263261352', '1044517323', '3500366177', '627247388', '8149663261',
        #                    '3283064530',
        #                    '3512244413', '194763870', '4140774272', '3734749188', '347784519', '5625418090',
        #                    '2247284586',
        #                    '4723695082', '1232869925', '18786556', '1419492326', '1319672519', '1701505588',
        #                    '6095871555',
        #                    '3054256207', '5884237349', '3610524853', '549166851', '7442411991', '180909770',
        #                    '1293940469',
        #                    '287833113', '740013852', '2294570301', '594852861', '410514859', '7230887429', '2283745543',
        #                    '4746437', '5606732930', '1666189105', '17297519', '3112003535', '364567372', '693815',
        #                    '12720824'],
        #     '3040634': ['397567', '29848760', '24817899', '6698793255', '248041440', '1248535', '2219567394',
        #                 '31725905',
        #                 '338685163', '806853', '2137525529', '1500703397', '47257476', '1489446154', '6887645358',
        #                 '1012042738', '242909896', '1254810641', '9731861567', '1183259914', '1084807', '362789392',
        #                 '374357625', '6275292500', '9426224017', '24240550', '4787743290', '253944995', '185507912',
        #                 '28417283', '3412584736', '1316352961', '23585926', '3924149854', '3621906702', '323036143',
        #                 '697640432', '48187682', '1666099', '11356279', '4498960541', '4009415770', '40740515',
        #                 '4375373461', '770095', '2974661850', '702724', '256023684', '5333770065', '195021764',
        #                 '3565984864', '916689', '5414738534', '330508257', '2218987982', '2176592301', '339966146',
        #                 '2970822', '18012145', '36889302', '29109254', '324471314', '4366277', '269361977', '40360284',
        #                 '36900423', '250888750', '227694298', '4184253944', '6683852608', '2119007300', '3971667170',
        #                 '1441140644', '22049347', '386884160', '18341606', '210615194', '5453598421', '20695132',
        #                 '38283022', '4140774272', '2905334413', '3041171', '186559', '393004090', '36851031',
        #                 '4423354912',
        #                 '1734062024', '284029973', '245662611', '577556512', '1510676723', '9877232', '1529761677',
        #                 '726445', '1088907', '227176561', '349413719', '795957', '3372827', '5483101808', '389922208',
        #                 '233747513', '367858399', '55133165', '32575', '7744479224', '2913247', '1345919', '269204263',
        #                 '304768948', '7066814', '25961231', '5727311186', '2142578', '8956205850', '24179557',
        #                 '34732714',
        #                 '12622159', '218692437', '942422434', '3285835042', '29431944', '3670624004', '1124706329',
        #                 '8604385621', '2032892388', '308412469', '1431295721', '2315931169', '4024158035', '20348279',
        #                 '7423377680', '3299193159', '1586151436', '207157081'],
        #     '821792': ['7956064726', '6649098677', '8145349422', '50696951', '14452790', '4578760057', '2069628',
        #                '5527672749', '8214381704', '4134007185', '1132752377', '4858281667', '3954665497', '3182242055',
        #                '2866548466', '8608056612', '1642322358', '5862818432', '1433954278', '3626544152', '226537858',
        #                '143799873', '5477966810', '2123842781', '2057301277', '505414063', '259165067', '397218463',
        #                '232638168', '13743559519', '4056455267', '31832622', '2075507035', '2873357480', '529914741',
        #                '624010391', '8905725322', '5315784458', '13305146388', '5974280613', '2279430795', '8435264084',
        #                '29720685', '47586672', '22823963', '7403953255', '193845803', '1420511546', '4919536689',
        #                '539962112', '14497357', '1474272023', '332580078', '1279057162', '1315493935', '10814562',
        #                '329119450', '5022991215', '271881168', '8149875666', '2049692', '1004897257', '8631266654',
        #                '1497683675', '4140774272', '976576762', '442466798', '1291954220', '7545243405', '1513382676',
        #                '4933476848', '40414991', '8639988728', '11769859300', '2120586995', '8288375903', '2110659286',
        #                '4118962651', '665178', '14837682', '3321471281', '14063300204', '6913698315', '375451348',
        #                '5420847187', '1300282112', '8157105658', '2305408324', '1071530569', '1317815783', '284974401',
        #                '608177031', '6499097262', '611329946', '1491041754', '699279424', '7456333737', '4224354582',
        #                '1262382231', '1690110', '1315515061', '4481400963', '778480673', '33961614', '193097570',
        #                '624827558', '1613532', '480435020', '2772879867'],
        #     '144166': ['254638430', '4838673798', '4299914666', '747167', '1792153914', '1756097708', '912750',
        #                '1388888388', '1664883', '40983733', '4960266234', '1144891459', '5373249748', '4140774272',
        #                '38152707', '3511568', '2247284586', '577047512', '53680545', '2305618880', '4256402774',
        #                '4373691550', '1517161', '730854', '40540280', '905818732', '2291816980', '7396105378',
        #                '8160927835', '51064084', '817191', '3112003535', '4059253717'],
        #     '1982324715': ['12423841858', '17625021', '228160939', '3626469223', '311915065', '8149663261',
        #                    '6677928006',
        #                    '3546078500', '6096606911', '7636563448', '4140774272', '1071058207', '1103098445',
        #                    '4653296425', '2247284586', '4840900146', '5837854733', '1482098376', '5704143146',
        #                    '2461472888', '210292377', '1972502008', '4754582721', '180909770', '6932942726',
        #                    '529001266',
        #                    '1204256355', '1537150866', '1083669962', '13440145730', '14455940', '1666189105',
        #                    '3112003535'],
        #     '5973413688': ['16852059', '3458557203', '4108206739', '7095132268', '1510512338', '343444689', '2325145',
        #                    '4140774272', '7583675650', '9695983779', '13039431', '6711731354', '184570664',
        #                    '1349968501',
        #                    '2253914110', '5964238739', '2499310937', '298880468', '4904295672', '3154654696',
        #                    '22911378069', '2095709191', '5563288237', '5545290181', '1409434299', '15408976',
        #                    '8160414312',
        #                    '3099080', '9157789565', '3969068361', '8267379026', '8655216174', '14110372239'],
        #     '29109254': ['397567', '3475000', '31859066', '2209163753', '2514245', '186227089', '894488383',
        #                  '1916980974',
        #                  '1186210811', '187651037', '2392409', '202527574', '279550431', '8955981049', '4211669',
        #                  '2088116695', '284423868', '1587973670', '2974210898', '804235260', '9774386791', '240875458',
        #                  '180926338', '1694909', '48566213', '6279781120', '673035', '770095', '38209966', '7099360585',
        #                  '177271342', '29122457', '1588352995', '4302218128', '1154024736', '265936268', '1292759474',
        #                  '36266700', '1951475573', '13884857', '350343811', '51233957', '488805318', '840578',
        #                  '1323423656', '46709065', '337481180', '233339601', '40461882', '1154369246', '700105',
        #                  '1830961690', '4417464', '3312547657', '205222598', '189286417', '745288', '27031815',
        #                  '597310',
        #                  '3317350494', '1251887260', '5909885110', '9257955', '1286554715', '1548164179', '489653385',
        #                  '2151234866', '2780167', '33010082', '7783190638', '48392355', '662394', '760724',
        #                  '2158273081',
        #                  '4140774272', '18044860', '2069033901', '5552124', '1925901428', '1352598106', '411812153',
        #                  '201838919', '249853676', '1195824', '1206031687', '30068217', '63107', '233508693',
        #                  '281963674',
        #                  '1451423967', '665178', '36924174', '29275820', '5411146735', '6882672', '323984270',
        #                  '1360348',
        #                  '197277256', '1192708097', '3677398', '7315610', '518107351', '14527855896', '1516158159',
        #                  '180286006', '11557659', '1579861', '1345919', '189033', '3578773020', '5076095', '7066814',
        #                  '2165750784', '187726213', '1614272919', '17586236964', '43505638', '1167071700', '812006',
        #                  '1287857015', '30114353', '683673', '615653222', '2473850', '1503584388', '3040634', '131780',
        #                  '178796625', '37951354', '1613532', '4853921776', '5400703774', '12539291', '1962675251',
        #                  '1986988551', '8415304634'],
        #     '181603649': ['1479668705', '203617153', '53198861', '1364216022', '2155039811', '1167569063', '538247977',
        #                   '789715', '39476343', '1423714133', '2247248695', '4867935561', '359128864', '2911167431',
        #                   '1232502473', '1359312618', '2202017111', '1137410081', '4307548', '598332293', '42502137',
        #                   '36730212', '4009415770', '7099360585', '2395073', '502196572', '254366923', '37015818',
        #                   '715127', '739155475', '1995422379', '9120333279', '1852791', '6251652152', '1386007889',
        #                   '209687062', '7350261775', '7094807471', '311082434', '2213263109', '269883416', '760120728',
        #                   '712883', '211940769', '1560885089', '37243812', '506515869', '41240685', '1474272023',
        #                   '13723529', '23862106', '19388350', '7216033216', '669060677', '492383911', '5895750344',
        #                   '5106304181', '4140774272', '8208701634', '2059124691', '1195824', '54650679', '6998527767',
        #                   '1490084763', '38304731', '1467477592', '273481', '257500875', '665178', '413239691',
        #                   '14837682',
        #                   '2178788', '1324513796', '2926016034', '2238487220', '18157923', '3029421754', '2273025404',
        #                   '2013103', '2026348353', '309386016', '466642660', '1158503353', '1550010691', '10981816535',
        #                   '210639273', '20346952', '1446721496', '2314293467', '463872167', '924806413', '7994756175',
        #                   '7968931487', '683673', '1491934611', '2989218743'],
        #     '4790080914': ['254638430', '4389753838', '2209500908', '1415338585', '7894358215', '2328703685',
        #                    '360553313',
        #                    '4472310414', '830462905', '1915930155', '7813223571', '2235450120', '500986677',
        #                    '735364805',
        #                    '219512941', '4796490648', '3537056619', '1174408169', '4140774272', '2021689546',
        #                    '8093009140',
        #                    '5773617414', '5582380312', '2247284586', '7826134', '5463489494', '5837854733',
        #                    '4869747925',
        #                    '5755935873', '5715558974', '6195857933', '4256402774', '235647525', '532363965',
        #                    '1670596252',
        #                    '2135538723', '8538973908', '16848010781', '3210614388', '4280086057', '6206992286',
        #                    '1249031096', '2278979158', '3152700286', '2104573787', '3245619944', '1653072395',
        #                    '5682855152', '5944074989', '5496755053', '4565612697', '5989179836', '645959448',
        #                    '5889501884',
        #                    '8690951798', '2239968233', '3112003535', '1264753920', '4183497580', '2282969733',
        #                    '17297519',
        #                    '1198405466', '1329519950', '448757902'],
        #     '1666189105': ['4175344695', '2242403369', '228160939', '6504853737', '17625021', '8149663261', '627247388',
        #                    '1384701242', '562163371', '6621838456', '1206893185', '4140774272', '5625418090',
        #                    '2247284586',
        #                    '2305618880', '1561319877', '48066069', '3054256207', '1044590017', '180909770',
        #                    '2946125248',
        #                    '1982324715', '4523766690', '6770037', '410514859', '4398995298', '3653980192', '5606732930',
        #                    '17297519', '3112003535', '1282893695', '375451348'],
        #     '14497357': ['1666541927', '192557117', '4361766512', '3968453', '36926622', '196439563', '6297777235',
        #                  '224390943', '1045500522', '39267895', '461921313', '5384536180', '4140774272', '176157529',
        #                  '2215398', '12259', '637281822', '209322047', '36745209', '2954056694', '14747873', '3579746',
        #                  '330154513', '47796348', '182882752', '821792', '273481', '36889302', '4681214', '187910517',
        #                  '659786773', '1605027904', '268840081', '307250290', '1360348', '287823659', '1359643',
        #                  '2848223499', '7009951', '7231293428', '1580892975'],
        #     '223257503': ['4473010216', '23862106', '1915019098', '770095', '5384046614', '6754668979', '53198861',
        #                   '8496338166', '2060803551', '6794871187', '4140774272', '31871868', '370178658', '1103700775',
        #                   '1187338738', '5452786461', '4669375712', '16049363', '4704766831', '4247299057', '179333653',
        #                   '745288', '665178', '4402574', '37243812', '2291313913', '327459833', '1474272023'],
        #     '17297519': ['228160939', '8149663261', '17490932', '1206893185', '4140774272', '3734749188', '893364',
        #                  '5837854733', '883081', '55568335', '104830957', '48066069', '3054256207', '1044590017',
        #                  '180909770', '3045962415', '2294570301', '4790080914', '1666189105', '2008415702',
        #                  '3112003535'],
        #     '375451348': ['254638430', '2206319048', '240550685', '2259668205', '4186690255', '43066805', '228160939',
        #                   '219512941', '976423076', '2291954725', '4037175612', '6971218472', '5931993381', '45638129',
        #                   '2366998746', '4140774272', '393133616', '2332186786', '7875234074', '8055224300',
        #                   '282755609',
        #                   '287272425', '7826134', '272019017', '290275764', '4656561217', '3657761652', '3441411656',
        #                   '8396513790', '6793060911', '13856404533', '256234785', '7345829806', '4232341101',
        #                   '597909584',
        #                   '4559562355', '47586672', '190451357', '24794745', '29783559107', '2171332046', '3984206815',
        #                   '1646405764', '821792', '2110659286', '207193604', '30567904', '1059876233', '48412474',
        #                   '646398369', '2057301277', '10843156', '1666189105', '315441903', '6347148387', '2130678945',
        #                   '369569307', '17753295'],
        #     '26001306': ['1151480419', '1915019098', '146026992', '682270', '4009415770', '5746966423', '6811263806',
        #                  '2049692', '2069628', '2226538105', '4140774272', '135882', '4211550169', '11460482398',
        #                  '1408387', '36695455', '189704718', '1525013112', '9610438064', '5123970', '39772846',
        #                  '651311165', '1496763', '1186210811', '287901815', '14674999', '356441319', '10254252438',
        #                  '9446992774', '3590081889', '3669263296', '29815693', '745288', '575559013', '14837682',
        #                  '1818344246', '7999123919', '226878586', '644194128', '9421866432', '130640', '20697636',
        #                  '3706272904', '1474272023', '2003573397'], '25937844225': ['25360069272', '4140774272']}
        # intersection_data = {
        #     # '4140774272': ['254638430', '42502137', '3037318828', '4009415770', '682270', '266913770', '228160939',
        #     #                '17625021', '2049692', '38569514', '3598953314', '41069358', '2069628', '3537056619',
        #     #                '1916698080', '1473858700', '529914741', '1339999012', '5780272989', '34810713',
        #     #                '5625418090',
        #     #                '2293895854', '7582174347', '2305618880', '5573484158', '1186210811', '2134439879',
        #     #                '33961614',
        #     #                '3906768725', '270339026', '804837047', '54650679', '29720685', '5606253289', '3040634',
        #     #                '530984452', '1598311938', '1044590017', '1474272023', '8935718315', '821792', '144166',
        #     #                '1982324715', '5973413688', '273481', '1467477592', '2947007029', '14837682', '29109254',
        #     #                '181603649', '10239933', '6862672481', '4790080914', '1666189105', '11632197068', '14497357',
        #     #                '223257503', '17297519', '375451348', '26001306', '25937844225'],
        #     '254638430': ['5625418090', '4790080914', '17625021', '375451348', '3537056619', '144166'],
        #     '42502137': ['273481', '181603649', '54650679'], '3037318828': ['1474272023'],
        #     '4009415770': ['273481', '181603649', '3040634', '1474272023', '26001306', '529914741'],
        #     '682270': ['1467477592', '2134439879', '266913770', '2049692', '2069628', '3537056619'],
        #     '266913770': ['2069628', '2049692'], '228160939': ['17297519', '375451348'],
        #     '2049692': ['273481', '821792', '1467477592', '682270', '266913770', '1474272023', '2069628', '26001306'],
        #     '38569514': ['14837682'], '2069628': ['821792', '682270', '266913770', '1474272023', '2049692', '26001306'],
        #     '3537056619': ['254638430', '682270', '4790080914', '5625418090'],
        #     '529914741': ['29720685', '4009415770', '821792', '14837682'], '5780272989': ['270339026'],
        #     '5625418090': ['254638430', '1666189105', '3598953314', '1044590017', '2305618880', '3537056619'],
        #     '2293895854': ['33961614'], '2305618880': ['5625418090', '1666189105', '144166'],
        #     '1186210811': ['29109254', '273481', '54650679'], '2134439879': ['682270'],
        #     '33961614': ['821792', '14837682', '5606253289'],
        #     '1474272023': ['273481', '821792', '1467477592', '3037318828', '181603649', '4009415770', '266913770',
        #                    '54650679', '29720685', '223257503', '2049692', '2069628', '26001306'],
        #     '29720685': ['529914741', '821792', '1474272023', '14837682'],
        #     '54650679': ['273481', '42502137', '181603649', '1474272023', '1186210811'], '5606253289': ['33961614'],
        #     '1044590017': ['5625418090', '1666189105', '17297519'], '3040634': ['29109254', '4009415770'],
        #     '821792': ['33961614', '14837682', '29720685', '14497357', '2049692', '375451348', '2069628', '1474272023',
        #                '529914741'], '144166': ['254638430', '2305618880'],
        #     '1982324715': ['1666189105', '17625021', '228160939'], '29109254': ['3040634', '1186210811'],
        #     '181603649': ['273481', '1467477592', '42502137', '14837682', '4009415770', '54650679', '1474272023'],
        #     '4790080914': ['254638430', '3537056619', '17297519'],
        #     '1666189105': ['5625418090', '228160939', '17625021', '17297519', '1044590017', '2305618880', '375451348',
        #                    '1982324715'], '14497357': ['273481', '821792'], '223257503': ['1474272023'],
        #     '17297519': ['1666189105', '4790080914', '1044590017', '228160939'],
        #     '375451348': ['254638430', '1666189105', '821792', '228160939'],
        #     '26001306': ['14837682', '4009415770', '682270', '2049692', '2069628', '1474272023', '1186210811']}
        # for user_id, data in intersection_data.items():
        #     temp = []
        #     for i in data:
        #         if i in intersection_data.keys():
        #             temp.append(i)
        #     result[user_id] = temp
        # the_result = {}
        # for k, v in result.items():
        #     temp = []
        #     user_data = self.ud.user_data_base_user_id(k)
        #     k_name = user_data["user_name"]
        #     k_full_name = user_data["full_name"]
        #     for g in v:
        #         user_data = self.ud.user_data_base_user_id(g)
        #         name = user_data["user_name"]
        #         full_name = user_data["full_name"]
        #         temp.append({"name": name, "full_name": full_name})
        #     the_result[k_name + " " + k_full_name] = temp
        # return the_result
        result = []
        # user_id = "1474272023"
        # for data in [intersection_data[user_id]]:
        for user_id, data in intersection_data.items():
            up = [user_id]
            self.get_group(my_id, result, up, data, intersection_data, all_data)
        print(result)
        the_result = []
        for i in result:
            temp = []
            for e in i:
                user_data = self.ud.user_data_base_user_id(e)
                name = user_data["user_name"]
                full_name = user_data["full_name"]
                temp.append(name + " " + full_name)
            the_result.append(temp)
        return the_result

    def get_group(self, my_id, result, up, data, intersection_data, all_data):
        temp_up = copy.deepcopy(up)
        while data:
            print("up", temp_up)
            print("data", data)
            now = data.pop(0)
            count = 0
            if now in all_data.keys():
                for have in temp_up:
                    if now in all_data[have] and have in all_data[now]:
                        count += 1
                    else:
                        print("err", now, have)
            if now in intersection_data.keys() and count == len(temp_up):
                temp = []
                for i in data:
                    if i in all_data[now] and i in intersection_data and now in all_data[i]:
                        count = 0
                        # 和之前的都是好友关系
                        for have in temp_up:
                            if i in all_data[have] and have in all_data[i]:
                                count += 1
                            else:
                                print("err", i, have)
                        if count == len(temp_up):
                            temp.append(i)
                if len(temp) > 0:
                    print("up", temp_up)
                    print("now", now)
                    print("temp", temp)
                    temp_up.append(now)
                    self.get_group(my_id, result, temp_up, temp, intersection_data, all_data)
                else:
                    temp_up.append(my_id)
                    temp_up = list(set(temp_up))
                    temp_up.sort()
                    if temp_up not in result and len(temp_up) > 3:
                        print("result", temp_up)
                        result.append(temp_up)
                    break
            if data:
                self.get_group(my_id, result, temp_up, data, intersection_data, all_data)

    def same_friends(self, name):
        user_data = self.ud.user_data_base_username(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        all_user = friends_id
        all_data = {}
        intersection_data = {}
        for user in all_user:
            t_friend = self.ud.friends(user)
            if t_friend is False:
                continue
            t_friend = [f["id"] for f in t_friend]
            try:
                t_friend.remove(my_id)
            except:
                pass
            all_data[user] = t_friend
        for id, data in all_data.items():
            data = intersection(friends_id, data)
            if len(data) == 0:
                continue
            intersection_data[id] = data
        return intersection_data

    def friends_friends_top(self, name):
        user_data = self.ud.user_data_base_username(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        following = self.ud.following(my_id)
        following_id = [f["id"] for f in following]
        all_user = friends_id
        all_data = {}
        for user in all_user:
            t_friend = self.ud.friends(user)
            if t_friend is False:
                continue
            t_friend = [f["id"] for f in t_friend]
            try:
                t_friend.remove(my_id)
            except:
                pass
            all_data[user] = t_friend
        all_friend_friends = []
        for user_id, data in all_data.items():
            for data_ in data:
                all_friend_friends.append(data_)
        _all_friend_friends = list(set(all_friend_friends).difference(set(friends_id)))
        friend_friend_list = []
        friend_friend_mapping = {}
        for friend_friend in all_friend_friends:
            if friend_friend in _all_friend_friends and friend_friend not in following_id:
                if friend_friend in friend_friend_list:
                    friend_friend_mapping[friend_friend] += 1
                else:
                    friend_friend_list.append(friend_friend)
                    friend_friend_mapping[friend_friend] = 1
        return {"list": sort_by_value(friend_friend_mapping), "mapping": friend_friend_mapping}

    def friends_friend_follower_top(self, name):
        user_data = self.ud.user_data_base_username(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        following = self.ud.following(my_id)
        following_id = [f["id"] for f in following]
        all_user = friends_id
        all_data = {}
        for user in all_user:
            t_friend = self.ud.friends(user)
            if t_friend is False:
                continue
            try:
                t_friend.remove(my_id)
            except:
                pass
            t_f_list = []
            for t_f in t_friend:
                t_f_d = self.ud.user_data_base_user_id(t_f["id"])
                if t_f_d:
                    t_f_list.append({"id": t_f["id"], "follower_count": t_f_d["follower_count"]})
            all_data[user] = t_f_list
        print(all_data)
        result = {}
        for user_id, data in all_data.items():
            for i in data:
                if i["id"] not in friends_id and i not in following_id and i["id"] not in result.keys():
                    result[i["id"]] = i["follower_count"]

        print(result)
        return {"list": sort_by_value(result), "mapping": result}

    def friends_following_top(self, name):
        user_data = self.ud.user_data_base_username(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        following = self.ud.following(my_id)
        following_id = [f["id"] for f in following]
        all_user = friends_id
        all_data = {}
        for user in all_user:
            t_following = self.ud.following(user)
            if t_following is False:
                continue
            t_following = [f["id"] for f in t_following]
            try:
                t_following.remove(my_id)
            except:
                pass
            all_data[user] = t_following
        result = {}
        result_list = []
        for user_id, data in all_data.items():
            for i in data:
                if i not in friends_id and i not in following_id:
                    if i in result_list:
                        result[i] += 1
                    else:
                        result_list.append(i)
                        result[i] = 1
        print(result)
        return {"list": sort_by_value(result), "mapping": result}

    def my_friends_know_a_friends_top(self, name):
        user_data = self.ud.user_data_base_username(name)
        my_id = user_data["id"]
        friends = self.ud.friends(my_id)
        friends_id = [f["id"] for f in friends]
        following = self.ud.following(my_id)
        following_id = [f["id"] for f in following]
        all_user = friends_id
        all_data = {}
        for user in all_user:
            t_friend = self.ud.friends(user)
            if t_friend is False:
                continue
            t_friend = [f["id"] for f in t_friend]
            try:
                t_friend.remove(my_id)
            except:
                pass
            all_data[user] = t_friend
        result = {}
        for user_id, data in all_data.items():
            t_user_friends_list = []
            for t_user_id, t_data in all_data.items():
                if t_user_id != user_id:
                    for t_f in t_data:
                        t_user_friends_list.append(t_f)
            try:
                t_user_friends_list.remove(user_id)
            except:
                pass
            t_result = {}
            t_result_list = []
            for f_id in t_user_friends_list:
                if f_id in data:
                    if f_id in t_result_list:
                        t_result[f_id] += 1
                    else:
                        t_result_list.append(f_id)
                        t_result[f_id] = 1
            print(t_result)
            result[user_id] = {"list": sort_by_value(t_result), "mapping": t_result}
        return result


def my_all_report(user):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '12MmAW4HNl4B3bkFMYI14Em53exW3EL_1sgCRSp4UIW0')
    analysis = Analysis()
    result = analysis.my_all(user)
    data = []
    for id, i in result.items():
        if i:
            data.append(
                [i["name"], i["full_name"], i["follower_follower"], i["following_follower"], i["following_following"],
                 i["follower_following"], i["friends_friends"]])
    sheet = GS.update_sheet(user, "A2:G", data)
    print(sheet)


def my_group(user):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1S6tTRyRExGxyGU807gLRmvxYiNmBA5UAin131FTt4LA')
    analysis = Analysis()
    data = analysis.friends_group(user)
    result = []
    for v in data:
        temp = []
        for e in v:
            temp.append(e["name"] + " " + e["full_name"])
        result.append(temp)
    print(len(result))
    sheet = GS.update_sheet(user + "_test1", "A2:Z", result)
    print(sheet)


def my_group_test(user):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1S6tTRyRExGxyGU807gLRmvxYiNmBA5UAin131FTt4LA')
    analysis = Analysis()
    data = analysis.friends_group(user)
    sheet = GS.update_sheet(user + "_test1", "A2:Z", data)
    print(sheet)


def friends_friends_top_report(name):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1YLA3wxZwZJSM_yjwi4Sey1L1-y__ufwovw6mPurApCc')
    ud = UserData()
    analysis = Analysis()
    data = analysis.friends_friends_top(name)
    data = data["mapping"]
    result = []
    for k, v in data.items():
        u_d = ud.user_data_base_user_id(k)
        if u_d is False:
            continue
        n = u_d["user_name"]
        f_n = u_d["full_name"]
        result.append([n + " " + f_n, v])
    sheet = GS.update_sheet(name + "_好友的好友推荐", "A1:Z", result)
    print(sheet)


def friends_following_top_report(name):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1YLA3wxZwZJSM_yjwi4Sey1L1-y__ufwovw6mPurApCc')
    ud = UserData()
    analysis = Analysis()
    data = analysis.friends_following_top(name)
    data = data["mapping"]
    result = []
    for k, v in data.items():
        u_d = ud.user_data_base_user_id(k)
        if u_d is False:
            continue
        n = u_d["user_name"]
        f_n = u_d["full_name"]
        result.append([n + " " + f_n, v])
    sheet = GS.update_sheet(name + "_好友following推荐", "A1:Z", result)
    print(sheet)


def friends_friend_follower_top_report(name):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1YLA3wxZwZJSM_yjwi4Sey1L1-y__ufwovw6mPurApCc')
    ud = UserData()
    analysis = Analysis()
    data = analysis.friends_friend_follower_top(name)
    data = data["mapping"]
    result = []
    for k, v in data.items():
        u_d = ud.user_data_base_user_id(k)
        if u_d is False:
            continue
        n = u_d["user_name"]
        f_n = u_d["full_name"]
        result.append([n + " " + f_n, v])
    sheet = GS.update_sheet(name + "_好友的好友根据follower推荐", "A1:Z", result)
    print(sheet)


def same_friends_report(name):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1YLA3wxZwZJSM_yjwi4Sey1L1-y__ufwovw6mPurApCc')
    ud = UserData()
    analysis = Analysis()
    data = analysis.same_friends(name)
    result = []
    for k, v in data.items():
        u_d = ud.user_data_base_user_id(k)
        if u_d is False:
            continue
        n = u_d["user_name"]
        f_n = u_d["full_name"]
        temp = [n + " " + f_n]
        for i in v:
            t_u_d = ud.user_data_base_user_id(i)
            if t_u_d is False:
                continue
            t_n = t_u_d["user_name"]
            t_f_n = t_u_d["full_name"]
            temp.append(t_n + " " + t_f_n)
        result.append(temp)
    sheet = GS.update_sheet(name + "_共同好友", "A1:ZZ", result)
    print(sheet)


def my_friends_know_a_friends_top_report(name):
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1YLA3wxZwZJSM_yjwi4Sey1L1-y__ufwovw6mPurApCc')
    ud = UserData()
    analysis = Analysis()
    data = analysis.my_friends_know_a_friends_top(name)
    result = []
    for k, v in data.items():
        u_d = ud.user_data_base_user_id(k)
        if u_d is False:
            continue
        n = u_d["user_name"]
        f_n = u_d["full_name"]
        temp = [n + " " + f_n]
        if v["mapping"]:
            for i, c in v["mapping"].items():
                t_u_d = ud.user_data_base_user_id(i)
                if t_u_d is False:
                    continue
                t_n = t_u_d["user_name"]
                t_f_n = t_u_d["full_name"]
                temp.append(t_n + " " + t_f_n + " " + str(c))
        result.append(temp)
    sheet = GS.update_sheet(name + "_a_好友认识我好友", "A1:ZZ", result)
    print(sheet)


if __name__ == "__main__":
    # my_all_report("ter.zhao")
    analysis = Analysis()
    # a = analysis.friends_group("yuankeke001")
    # a = analysis.friends_friends_top("yuankeke001")
    # a = analysis.friends_friend_follower_top("yuankeke001")
    # a = analysis.friends_following_top("yuankeke001")
    # a = analysis.my_friends_know_a_friends_top("yuankeke001")
    # a = analysis.friends_friends_top("ter.zhao")
    # print(a)
    # my_group_test("ter.zhao")
    # my_group_test("yuankeke001")
    # my_group("yuankeke001")
    # my_group_id()
    # friends_friends_top_report("yuankeke001")
    # friends_friend_follower_top_report("yuankeke001")
    # friends_following_top_report("yuankeke001")
    # same_friends_report("yuankeke001")
    my_friends_know_a_friends_top_report("yuankeke001")
    # friends_friends_top_report("ter.zhao")
    # friends_friend_follower_top_report("ter.zhao")
    # friends_following_top_report("ter.zhao")
    # same_friends_report("ter.zhao")
    my_friends_know_a_friends_top_report("ter.zhao")
