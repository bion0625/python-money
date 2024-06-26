import pandas as pd
import pymysql, re
from datetime import datetime, timedelta

# 05_StockPriceAPI/Investar/Analyzer.py
class MarketDB:
    def __init__(self):
        """생성자: MariaDB 연결 및 종목코드 딕셔너리 생성"""
        self.conn = pymysql.connect(host='localhost', user='root', 
                                    password='snake.land.', db='INVESTAR', charset='utf8')
        self.codes = {}
        self.get_comp_info()

    def __del__(self):
        """소멸자: MariaDB 연결 해제"""
        self.conn.close()
    
    def get_comp_info(self):
        """company_info 테이블에서 읽어와서 codes에 저장"""
        sql = "SELECT * FROM company_info"
        krx = pd.read_sql(sql, self.conn)
        for idx in range(len(krx)):
            self.codes[krx['code'].values[idx]] = krx['company'].values[idx]
    def get_daily_price(self, code, start_date=None, end_date=None): # 인수=None 형식을 사용하면 인숫값이 주어지지 않았을 때 기본값으로 처리한다.
        """KRX 종목별 시세를 데이터프레임 형태로 반환
            - code  : KRX 종목코드('005930') 또는 상장기업명('삼성전자')
            - start_date    : 조회 시작일('2020-01-01'), 미입력 시 1년 전 오늘
            - end_date      : 조회 종료일('2020-12-31'), 미입력 시 오늘 날짜
        """
        if (start_date is None): # 만일 조회시작일로 넘겨받은 인수가 None이면, 인수가 입력되지 않은 경우이므로 (아래 주석)
            one_year_ago = datetime.today() - timedelta(days=365)
            start_date = one_year_ago.strftime('%Y-%m-%d') # 1년 전 오늘 날짜로 %Y-%m-%d 형식의 문자열로 처리한다.
            print("start_date is initialized to '{}'".format(start_date))
        else:
            start_lst = re.split('\D+', start_date)
            if(start_lst[0] == ''):
                start_lst = start_lst[1:]
            start_year = int(start_lst[0])
            start_month = int(start_lst[1])
            start_day = int(start_lst[2])
            if start_year < 1900 or start_year > 2200:
                print(f"ValueError: start_year({start_year:d}) is wrong.")
                return
            if start_month < 1 or start_month > 12:
                print(f"ValueError: start_month({start_month:d}) is wrong.")
                return
            if start_day < 1 or start_day > 31:
                print(f"ValueError: start_day({start_day:d}) is wrong.")
                return
            start_date = f"{start_year:04d}-{start_month:02d}-{start_day:02d}"
        
        if (end_date is None):
            end_date = datetime.today().strftime('%Y-%m-%d')
            print("start_date is initialized to '{}'".format(end_date))
        else:
            end_lst = re.split('\D+', end_date)
            if(end_lst[0] == ''):
                end_lst = end_lst[1:]
            end_year = int(end_lst[0])
            end_month = int(end_lst[1])
            end_day = int(end_lst[2])
            if end_year < 1900 or end_year > 2200:
                print(f"ValueError: end_year({end_year:d}) is wrong.")
                return
            if end_month < 1 or end_month > 12:
                print(f"ValueError: end_month({end_month:d}) is wrong.")
                return
            if end_day < 1 or end_day > 31:
                print(f"ValueError: end_day({end_day:d}) is wrong.")
                return
            end_date = f"{end_year:04d}-{end_month:02d}-{end_day:02d}"

        codes_keys = list(self.codes.keys()) # codes 딕셔너리로부터 키들을 뽑아서 키(종목코드) 리스트를 생성한다.
        codes_values = list(self.codes.values()) # codes 딕셔너리로부터 값들을 뽑아서 값(회사명) 리스트를 생성한다.
        if code in codes_keys: # 사용자가 입력한 값(code)이 '005930'이라서 키(종목코드) 리스트에 존재한다면 별도의 처리 없이 그대로 사용하면 된다.
            pass
        elif code in codes_values: # 사용자가 입력한 값(code)이 '삼성전자'라서 값(회사명) 리스트에 존재한다면 (아래 주석)
            idx = codes_values.index(code) # 값(회사명) 리스트에서 '삼성전자'의 인덱스를 구한 뒤, (아래 주석)
            code = codes_keys[idx] # 키(종목코드) 리스트에서 동일한 인덱스에 위치한 값('005930')을 구할 수 있다.
        else:
            print(f"ValueError: Code({code}) doesn't exist.")

        sql= f"SELECT * FROM daily_price WHERE code = '{code}'"\
            f" and date >= '{start_date}' and date <= '{end_date}'"
        print(sql) #del
        df = pd.read_sql(sql, self.conn) # 팬더스의 read_sql() 함수를 이용해 SELECT 결과를 데이터프레임으로 가져오면 정수형 인덱스가 별도로 생성된다.
        df.index = df['date'] # 따라서 df.index = df['date']로 데이터프레임의 인덱스를 date 칼럼으로 새로 설정해야 한다.
        
        return df
    