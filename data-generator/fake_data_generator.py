from faker import Faker
import numpy as np
from datetime import datetime, timedelta
import random

# #selected investors per company
INV_PER_COMP = 3
DURATION = 15

fake = Faker()

def fake_stock(size):
    # generate stock prices based on company size
    sticks = []
    base = 0.05 * size
    fluctuation = 0.2 * base
    today = datetime.now().date()
    for i in range(DURATION, 0, -1):
        max_price = np.random.uniform(base, base + fluctuation)
        min_price = np.random.uniform(base, base - fluctuation)
        stick = {
            "date"          : today - timedelta(days=i),
            "max_price"     : max_price,
            "min_price"     : min_price,
            "open_price"    : max(min_price, min(max_price, random.uniform(base - fluctuation, base + fluctuation))),
            "close_price"   : max(min_price, min(max_price, random.uniform(base - fluctuation, base + fluctuation)))
        }
        sticks.append(stick)
        
    return sticks

def fake_data(n_companies, n_investors, path):
    # generate investor data
    investor_name       = [fake.name() for i in range(n_investors)]
    investor_join_time  = [fake.date_between(start_date='-10y', end_date='today') for i in range(n_investors)]
    investor_account    = []
    investor_url        = []
    for name in investor_name:
        investor_account.append(str(name).replace(", ", "_").replace(" ", "_").replace("-", "_")+"_investor")
        investor_url.append("www."+str(name).lower().replace(", ", "_").replace(" ", "_").replace("-", "_")+".com")

    # generate company data
    company_name        = [fake.company() for j in range(n_companies)]
    establish_time      = [fake.date_between(start_date='-30y', end_date='today') for j in range(n_companies)]
    company_account     = []
    company_url         = []
    company_size        = np.random.randint(5, 1000, size=n_companies)
    company_investors   = dict() # company_investors[company] = [investor1, investor2, ...]
    company_stock       = dict() # company_stock[company] = [{date1, max1, min1, open1, close1}, {date2, max2, min2, open2, close2}, ...]
    for j in range(n_companies):
        name = company_name[j]
        company_url.append("www."+str(name).lower().replace(", ", "_").replace(" ", "_").replace("-", "_")+".com")
        company_account.append(str(name).replace(", ", "_").replace(" ", "_").replace("-", "_")+"_company")
        company_investors[company_name[j]] = [np.random.choice(investor_name) for i in range(INV_PER_COMP)]
        company_stock[company_name[j]] = fake_stock(company_size[j])

    df = {
        "investor_name"     : investor_name,
        "investor_join_time": investor_join_time,
        "investor_account"  : investor_account,
        "investor_url"      : investor_url,

        "company_name"      : company_name,
        "establish_time"    : establish_time,
        "company_account"   : company_account,
        "company_url"       : company_url,
        "company_size"      : company_size,

        "company_investors" : company_investors,
        "company_stock"     : company_stock
    }
    
    return df
    # df_csv = pd.DataFrame(df)
    # df_csv.to_csv(path, index=False)
    # print("Successful")
    
# path = "fake_data.csv"
# fake_data(100, 10, path)
# path = "small_data.csv"
# fake_data(10, 5, path)