import requests
import time
import subprocess
import datetime
import logging
import os

logger = logging.getLogger('streamlink_logger')
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

channel_id = os.getenv('CHANNEL_ID', '')
naver_api_url = f'https://api.chzzk.naver.com/service/v2/channels/{channel_id}/live-detail'
NID_AUT = os.getenv('NID_AUT', '')
NID_SES = os.getenv('NID_SES', '')
cookies = f"NID_AUT={NID_AUT}; NID_SES={NID_SES}"
USER_AGENT =  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Whale/3.23.214.17 Safari/537.36"

headers = {  
            "User-Agent": USER_AGENT,
            }

if cookies:
    headers['Cookie'] = cookies 

def check_naver_status():
    response = requests.get(naver_api_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('content', {}).get('status')
    else:
        logger.error(f"Error Status code: {response.status_code} Response: {response.text}")
        return None

def run_streamlink(channel_id):
    try:
        logger.info(f"치지직 라이브 녹화를 시작합니다!")
        suffix = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        subprocess.call(['streamlink', '--ffmpeg-copyts', '--plugin-dirs', '/home/callisto/plugins', f'https://chzzk.naver.com/live/{channel_id}', 'best', '--chzzk-cookies', f'{cookies}', '--output', f'/home/callisto/CHZZK-VOD/{suffix}.mp4'])
    except Exception as e:
        logger.error(f"Streamlink 실행 중 오류 발생: {e}")

def check_stream():
    while True:
        naver_status = check_naver_status()
        
        if naver_status == 'OPEN':
            response = response = requests.get(naver_api_url, headers=headers)
            title = response.json().get('content', {}).get('liveTitle')
            channel = response.json().get('content', {}).get('channel').get('channelName')
            print("")
            logger.info(f'[치지직 라이브] {channel}님의 방송이 시작되었습니다!')
            logger.info(f'방송 제목: {title}')
            logger.info(f'https://chzzk.naver.com/live/{channel_id}')
            print("")
            run_streamlink(channel_id)
            
            while check_naver_status() == 'OPEN':
                logger.info("Checking for close status")
                time.sleep(60)
        else:
            logger.info("OFFLINE! Checking again in 5 minutes.")
            time.sleep(300)

if __name__ == "__main__":
    check_stream()