import json
import requests

#카카오 앱 키
appkey = "카카오 앱 키"

#로그인 주소
login = "https://kauth.kakao.com/oauth/authorize?client_id=" + appkey + "&response_type=code&redirect_uri=https://localhost.com"

#로그인 완료 후 url창에 있는 code=를 복사, 붙여넣기
code[] = {"code0", "code1", "code2"}

#친구 목록 받아오는 주소
friendslist = "https://kauth.kakao.com/oauth/authorize?client_id=" + appkey + "&redirect_uri=https://localhost.com&response_type=code&scope=friends"

#친구 목록에서 UUID받아와서 저장
uuid[] = {"uuid0", "uuid1", }
#json파일 저장할 경로
jsonroot = "json 파일을 저장할 경로"

#토큰 가져와서 json파일로 저장(로그인 시 한번만 실행)
def get_token(num):
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": appkey,
        "redirect_uri": "https://localhost.com",
        "code": code[num]
    }

    response = requests.post(url, data=data)
    tokens = response.json()
    
    with open(jsonroot+str(num)+".json", "w") as fp:
        json.dump(tokens, fp)
    print(tokens)

#유저 정보 가져오기(로그인 만료 방지를 위해 로그인 시 한번 이상 실행해 주는 것이 좋음)
def get_user_info(num):
    with open(jsonroot+str(num)+".json", "r") as fp:
            ts = json.load(fp)
            url = "https://kapi.kakao.com/v2/user/me"
            headers = {
            "Authorization": "Bearer "+ts['access_token']
            }
            response = requests.get(url, headers=headers)
            print(response.json())

#토큰 갱신하기
def refresh_token(num):
    try:
        info = None
        ts = None
        with open(jsonroot+str(num)+".json", "r") as fp:
            ts = json.load(fp)
            url = "https://kauth.kakao.com/oauth/token"
            data = {
                "grant_type": "refresh_token",
                "client_id": appkey,
                "refresh_token": ts['refresh_token'],
            }
            response = requests.post(url, data=data)
            info = response.json()
            print(info)

            #토큰 새로고침 가능!
            if response.status_code == 200:
                keys = [key for key in info]
                print(keys)
                
                #리프레시 토큰 저장
                if "refresh_token" in keys:
                    ts['refresh_token'] = info['refresh_token']

                #리프레시 토큰 만료 기간 저장    
                if "refresh_token_expires_in" in keys:
                    ts['refresh_token_expires_in'] = info['refresh_token_expires_in']

                #토큰 저장    
                ts['access_token'] = info['access_token']
                with open(jsonroot+str(num)+".json", "w") as fp:
                    json.dump(ts, fp)
                print("token "+str(num)+" refreshed",info['expires_in'],"seconds left")
            else:
                print("refresh error",info)
    except Exception as e:
        print(e)
        return None       

#토큰 정보를 가져와서 토큰이 만료되었을 경우 토큰 갱신
def get_token_info(num):
    try:
        info = None
        ts = None
        with open(jsonroot+str(num)+".json", "r") as fp:
            ts = json.load(fp)
            
            url = "https://kapi.kakao.com/v1/user/access_token_info"
            headers = {
                "Authorization": "Bearer "+ts['access_token']
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                print("token alive")
                return None
            else:
                print(response.json())
                print("token dead, need to refresh")
                refresh_token(num)
            
    except Exception as e:
        print(e)
        return None


 #메시지 보내기   
def print_text(text,friend=None):
    try:
        #토큰 만료되었는지 먼저 확인
        if friend is None:
            get_token_info(0)
        else:
            get_token_info(friend)
            
        with open(jsonroot+"0.json", "r") as fp:
            ts = json.load(fp)

        #나에게 보내기
        if friend is None:
            url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
            headers = {
                "Authorization": "Bearer "+ts['access_token']
            }
            data = {
                "template_object": json.dumps({
                    "object_type": "text",
                    "text": text,
                    "link": {
                        "web_url": "https://developers.kakao.com",
                        "mobile_web_url": "https://developers.kakao.com"
                    },
                })
            }
            response = requests.post(url, headers=headers, data=data)
        else:
            url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
            headers = {
                "Authorization": "Bearer "+ts['access_token']
            }
            data = {
                "receiver_uuids": "[\""+uuid[friend]+"\"]",
                "template_object": json.dumps({
                    "object_type": "text",
                    "text": text,
                    "link": {
                        "web_url": "https://developers.kakao.com",
                        "mobile_web_url": "https://developers.kakao.com"
                    },
                })
            }
            response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return True
        else:
            print(response.json())
    except Exception as e:
        print(e)
        return None


def print_feed(source, title, friend=None):
    try:
        if friend is None:
            get_token_info(0)
        else:
            get_token_info(friend)
            
        if friend is None:
            with open(jsonroot+"0.json", "r") as fp:
                ts = json.load(fp)

                url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
                headers = {
                    "Authorization": "Bearer "+ts['access_token']
                }
                data = {
                    "template_object": json.dumps({
                        "object_type": "feed",
                        "content": {
                                "title": f"{title}",
                                "description": f"{source}",
                                "image_url": f"{source}",
                                "image_width": 640,
                                "image_height": 640,
                                "link": {
                                    "web_url": "http://www.daum.net",
                                    "mobile_web_url": "http://m.daum.net",
                                    "android_execution_params": "contentId=100",
                                    "ios_execution_params": "contentId=100"
                            }
                        }
                    })
                }
                response = requests.post(url, headers=headers, data=data)
        else:
            with open(jsonroot+f"{friend}.json", "r") as fp:
                ts = json.load(fp)

                url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
                headers = {
                    "Authorization": "Bearer "+ts['access_token']
                }
                data = {
                    "receiver_uuids": "[\"" + uuid[friend] + "\"]",
                    "template_object": json.dumps({
                        "object_type": "feed",
                        "content": {
                                "title": title,
                                "description": f"{source}",
                                "image_url": f"{source}",
                                "image_width": 640,
                                "image_height": 640,
                                "link": {
                                    "web_url": "http://www.daum.net",
                                    "mobile_web_url": "http://m.daum.net",
                                    "android_execution_params": "contentId=100",
                                    "ios_execution_params": "contentId=100"
                            }
                        }
                    })
                }
                response = requests.post(url, headers=headers, data=data)
        return True
    except Exception as e:
        print(e)
        return None

    
