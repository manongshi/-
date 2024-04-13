from flask import Flask, request, jsonify,render_template
import os
import json
import time
import requests
import pymongo
import JiaM
import math
import random
click = pymongo.MongoClient('mongodb://{}:{}@{}:{}/?authSource={}'.format("an","RL4WdfZiM8kSayhX","47.95.0.105","27017","an"))['an']['Ti']
click1 = pymongo.MongoClient('mongodb://{}:{}@{}:{}/?authSource={}'.format("an","RL4WdfZiM8kSayhX","47.95.0.105","27017","an"))['an']['Jihuo']
click2 = pymongo.MongoClient('mongodb://{}:{}@{}:{}/?authSource={}'.format("an","RL4WdfZiM8kSayhX","47.95.0.105","27017","an"))['an']['user']
app = Flask(__name__)
headers = {
            'Referer':'https://weiban.mycourse.cn/',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

@app.route('/')
def index():
    return render_template("login.html")

@app.route('/nei',methods=['get'])
def nei():
    return render_template("nei.html")

@app.route('/yz',methods=["POST"])
def yz():
    json_a = request.get_data()
    json_a = json.loads(json_a)
    data = json_a['data']
    condition = {
    "Jihuo":data,
    "Ci": {"$lt": 5}}
    res = click1.find_one(condition)
    da = {}
    try:
        res['_id'] = str(res['_id'])
        da['res'] = res
        da['state'] = '1'


        click1.update_one({'Jihuo':data},{'$inc': {'Ci': 1}})
    except Exception as e:
        da['state'] = '-1'
        da['data'] = str(e)
    return jsonify(da)

@app.route("/Shu",methods=['POST'])
def Shu():
    json_a = request.get_data()
    json_a = json.loads(json_a)
    School = json_a['School']
    user_name = json_a['user_name']
    user_mm = json_a['user_mm']
    yzm = json_a['yzm']
    now = json_a['now']
    data = {}
    try:
        def get_School():
            ti = time.time()
            url = f'https://weiban.mycourse.cn/pharos/login/getTenantListWithLetter.do?timestamp={ti*100000}'
            session = requests.session()
            res = session.post(url,headers=headers).content.decode()
            res = json.loads(res)
            dit = {}
            for i in res['data']:
                for j in i['list']:
                    dit[j['name']] = j['code']
            return dit

        tenantCode = get_School()[School]
        palod = {
            "userName": user_name,
            "password": user_mm,
            "tenantCode": tenantCode,
            "timestamp": now,
            "verificationCode": yzm
            }
        a = JiaM.login(palod)
        session = requests.session()
        ti = time.time()
        url = f'https://weiban.mycourse.cn/pharos/login/login.do?timestamp={ti * 100000}'
        dat = {
            'data': a
        }
        
        res = session.post(url,data=dat).content.decode()
        res = json.loads(res)
        data['data'] = res
        data['state'] = '1'
        data['payload'] = a

    except Exception as e:
        data['state'] = '-1'
        data['data'] = str(e)
    # user_xx = jsonify(data)
    return jsonify(data)


@app.route('/Kai',methods=['POST'])
def Kai():
    class An():
        def __init__(self):

            self.user = json.loads(request.get_json()['data'])  # 输入token查看



            print("token是:",self.user['token'])
            print('名字是:',self.user['nickName'])
            print("学号是:",self.user['uniqueValue'])
            self.tenantCode = 65000003  # 这里是学校的编码
            self.headers = {
                'X-Token': self.user["token"]
            }

        def get_userProjectId(self):
            url = f'https://weiban.mycourse.cn/pharos/index/listStudyTask.do?timestamp={time.time() * 1000}'
            data = {
                'tenantCode': self.tenantCode,
                'userId': self.user['userId']
            }
            res_userProjectId = requests.post(url=url, data=data, headers=self.headers).content.decode()
            self.userProjectId = json.loads(res_userProjectId)

        def get_categoryCode(self):
            self.get_userProjectId()
            url = f'https://weiban.mycourse.cn/pharos/usercourse/listCategory.do?timestamp={time.time() * 1000}'
            data = {
                'tenantCode': self.tenantCode,
                'userId': self.user['userId'],
                'userProjectId': self.userProjectId['data'][0]["userProjectId"],
                'chooseType': 3
            }
            res_categoryCode = requests.post(url=url, data=data, headers=self.headers).content.decode()
            j_res = json.loads(res_categoryCode)
            self.lis = []
            for i in j_res['data']:
                self.lis.append(i['categoryCode'])
            print(f'这是课程的总数:',len(self.lis))

        # 获取二级课程信息
        def get_second(self, categoryCode):

            url = f'https://weiban.mycourse.cn/pharos/usercourse/listCourse.do?timestamp={time.time() * 1000}'
            data = {
                'tenantCode': self.tenantCode,
                'userId': self.user['userId'],
                'userProjectId': self.userProjectId['data'][0]["userProjectId"],
                'chooseType': 3,
                'categoryCode': categoryCode
            }
            res_second = requests.post(url=url, data=data, headers=self.headers).content.decode()
            secondCorse = json.loads(res_second)['data']
            courseId = []
            for i in secondCorse:
                if int(i['finished']) == 2:
                    courseId.append(i['resourceId'])
            print(f"总共要刷{len(courseId)}个课")
            return courseId

        # 获取完成时候的代码
        def get_finshmm(self, courseId):
            ti = time.time()
            metoken_Url = f'https://weiban.mycourse.cn/pharos/usercourse/getCourseUrl.do?timestamp={ti * 1000}'

            data = {
                'tenantCode': self.tenantCode,
                'userId': self.user['userId'],
                'courseId': courseId,
                'userProjectId': self.userProjectId['data'][0]["userProjectId"]
            }
            res = requests.post(metoken_Url, data=data, headers=self.headers).content.decode()
            j = json.loads(res)
            ans = j['data'].split('?')[1].split('&')
            data = {}
            for i in ans:
                lis = i.split('=')
                data[lis[0]] = lis[1]
            j = 1
            while j < 14:
                print(f"1", end='')
                j += 1
                time.sleep(1)
            self.finish(data['methodToken'], data['userCourseId'])

        def finish(self, metoken, userCourseId):
            ti = time.time()
            callback = math.floor(random.uniform(0, 1) * 100000)
            url = f'https://weiban.mycourse.cn/pharos/usercourse/v1/{metoken}.do?callback={callback}&t={ti * 1000000}&userCourseId={userCourseId}&tenantCode={self.tenantCode}'
            data = {

            }
            res_finish = requests.post(url=url, headers=self.headers).content.decode()
            print("完成", res_finish)

        def start_study(self):
            self.get_categoryCode()
            sum = 0
            for a in self.lis:
                lis_course = self.get_second(a)
                print("长度", len(lis_course))

                for i in lis_course:
                    print('这是课程id', i)
                    url = f'https://weiban.mycourse.cn/pharos/usercourse/study.do?timestamp={time.time() * 1000}'
                    data = {
                        'tenantCode': self.tenantCode,
                        'userId': self.user['userId'],
                        'courseId': i,
                        'userProjectId': self.userProjectId['data'][0]["userProjectId"]
                    }
                    res_studyDo = requests.post(url=url, headers=self.headers, data=data).content.decode()
                    self.get_finshmm(i)

                    print()
                sum += 1

                print(f'完成第{sum}个课程')

        def Kao(self):
            self.get_userProjectId()
            url = f'https://weiban.mycourse.cn/pharos/exam/listPlan.do?timestamp={time.time() * 1000}'
            data = {
                'tenantCode': self.tenantCode,
                'userId': self.user['userId'],
                'userProjectId': self.userProjectId['data'][0]["userProjectId"]
            }
            # 获取考试的id和userExamPlanIds
            res_ = requests.post(url, headers=self.headers, data=data).content.decode()
            self.j_res = json.loads(res_)['data'][0]
            print('123', self.j_res)

        def preparDo(self):
            url = f'https://weiban.mycourse.cn/pharos/exam/preparePaper.do?timestamp={time.time() * 1000}'
            data = {
                'tenantCode': self.tenantCode,
                'userId': self.user['userId'],
                'userExamPlanId': self.j_res['id']
            }
            res = requests.post(url, headers=self.headers, data=data).content.decode()
            print('res', res)

        def get_questions(self):
            self.preparDo()
            url = f'https://weiban.mycourse.cn/pharos/exam/startPaper.do?timestamp={time.time() * 1000}'
            data = {
                'tenantCode': self.tenantCode,
                'userId': self.user['userId'],
                'userExamPlanId': self.j_res['id']
            }
            print("22222", data)
            res_ti = requests.post(url, data=data, headers=self.headers).content.decode()
            # print(res_ti)
            j_resTi = json.loads(res_ti)['data']['questionList']

            self.dit = {}
            for i in j_resTi:
                self.dit[i['id']] = []
                for j in i['optionList']:
                    self.dit[i['id']].append(j['id'])

        def do_work(self, questionId, answerIds):
            url = f'https://weiban.mycourse.cn/pharos/exam/recordQuestion.do?timestamp={time.time() * 1000}'
            data = {
                'tenantCode': self.tenantCode,
                'userId': self.user['userId'],
                'userExamPlanId': self.j_res['id'],
                'questionId': questionId,
                'useTime': random.randint(1, 700),
                'answerIds': answerIds,
                'examPlanId': self.j_res['examPlanId']
            }
            res = requests.post(url, data=data, headers=self.headers).content.decode()
            print('1111', res)

        def KaiKao(self):
            self.Kao()
            self.get_questions()
            po = 1
            wu = 1
            for k, y in self.dit.items():

                res = click.find_one({'questions_id': k})
                if res == None:
                    self.do_work(k, y[0])
                    print(f"没有这个题{wu}")
                    wu += 1
                else:
                    # print('1',','.join(res['data']))
                    self.do_work(k, ','.join(res['data']))
                time.sleep(1)
                print(f"这是第{po}题,还剩余{len(self.dit) - po}")
                po += 1

        def get_fen(self):
            url = f'https://weiban.mycourse.cn/pharos/exam/submitPaper.do?timestamp={time.time() * 1000}'
            data = {
                'tenantCode': self.tenantCode,
                'userId': self.user['userId'],
                'userExamPlanId': self.j_res['id']
            }
            fen = requests.post(url, data=data, headers=self.headers).content.decode()
            print(fen)

        def get_DaAnLis(self):
            url = f'https://weiban.mycourse.cn/pharos/exam/listHistory.do?timestamp={time.time() * 3}'
            data = {
                'tenantCode': self.tenantCode,
                'userId': self.user['userId'],
                'examPlanId': self.j_res['examPlanId'],
                'isRetake': 2
            }
            res = requests.post(url, data=data, headers=self.headers).content.decode()
            js = json.loads(res)['data']
            self.DaLis = []
            for i in js:
                self.DaLis.append(i['id'])

        def add_ti(self):
            self.get_DaAnLis()
            url = f'https://weiban.mycourse.cn/pharos/exam/reviewPaper.do?timestamp={time.time() * 3}'

            for i in self.DaLis:
                data = {
                    'tenantCode': self.tenantCode,
                    'userId': self.user['userId'],
                    'userExamId': i,
                    'isRetake': '2'
                }
                # print(data)
                res = requests.post(url, headers=self.headers, data=data).content.decode()
                # print(res)
                j_res = json.loads(res)['data']['questions']
                num = 0
                for i in j_res:
                    data = []
                    for j in i['optionList']:
                        if j['isCorrect'] == '1' or j['isCorrect'] == 1:
                            data.append(j['id'])
                    doc = {"questions_id": i['id'], 'data': data}
                    flag = click.count_documents({"questions_id": i['id']})

                    if flag >= 1:
                        num += 1
                        continue

                    click.insert_one(doc)
                print(f"共有{len(j_res)}个.重复{num}个")
                print("完成请退出")
        def get_g(self):
            url = f'https://weiban.mycourse.cn/pharos/my/getInfo.do?timestamp={time.time() * 3}'
            data = {
                'tenantCode': 65000003,
                'userId': self.user['userId']
            }
            res = requests.post(url,data=data,headers=self.headers).content.decode()
            t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            j_res = json.loads(res)['data']
            flag = click2.count_documents({'id':j_res['studentNumber']})
            if flag == 1:
                pass
            else:
                click2.insert_one({'nianJi':j_res['batchName'],'sexy':j_res['gender'],'xueyuan':j_res['orgName'],'id':j_res['studentNumber'],'realName':j_res['realName'],'zy':j_res['specialtyName'],'ti':t})

    a = An()
    a.start_study()
    a.KaiKao()
    a.get_fen()
    a.add_ti()
    a.get_g()
    return jsonify("完成")

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)