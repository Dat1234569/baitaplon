import requests 
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import schedule
import time

# Hàm lấy tin tức từ kenh14
def lay_tin_tuc():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0 Safari/537.36'}
    url = 'https://kenh14.vn/'
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.find_all('li', class_=lambda x: x and ('news' in x or 'item' in x or 'knswli' in x))
        print(f"Tìm thấy {len(articles)} bài viết")

        if len(articles) < 5:
            articles = soup.find_all('div', class_=lambda x: x and ('news' in x or 'story' in x))
            print(f"Tìm thấy {len(articles)} bài với cách khác")

        danh_sach = []

        for article in articles:
            try:
                title_tag = article.find('h3', class_=lambda x: x and 'title' in x)
                if not title_tag:
                    title_tag = article.find('h2') or article.find('a', href=True)
                title = title_tag.get_text(strip=True) if title_tag else 'Không có tiêu đề'

                desc_tag = article.find(lambda tag: tag.name in ['div', 'p', 'span']
                                        and tag.get('class') 
                                        and any('sapo' in c or 'desc' in c or 'summary' in c for c in tag.get('class')))
                if not desc_tag:
                    desc_tag = article.find('p')
                desc = desc_tag.get_text(strip=True) if desc_tag and len(desc_tag.get_text(strip=True)) > 20 else 'Không có mô tả'

                link_tag = article.find('a', href=True)
                link = link_tag['href'] if link_tag else ''
                if link and not link.startswith('http'):
                    link = 'https://kenh14.vn' + link

                img_tag = article.find('img', attrs={'src': True})
                img = img_tag['src'] if img_tag and 'src' in img_tag.attrs else 'Không có hình'

                danh_sach.append({
                    'Tiêu đề': title,
                    'Mô tả': desc,
                    'Hình ảnh': img,
                    'Link': link
                })

            except Exception as e:
                print(f"Lỗi lấy bài: {e}")
                continue

        if danh_sach:
            df = pd.DataFrame(danh_sach)
            file_name = f"kenh14_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            df.to_excel(file_name, index=False, engine='openpyxl')
            print(f"Đã lưu file: {file_name}")
        else:
            print("Không lấy được bài nào, kiểm tra lại!")

    except requests.RequestException as e:
        print(f"Lỗi lấy trang web: {e}")
    except Exception as e:
        print(f"Lỗi khác: {e}")
# Lấy tin tức ngay khi chạy code
lay_tin_tuc()
# Lên lịch chạy hằng ngày lúc 6h sáng
schedule.every().day.at("06:00").do(lay_tin_tuc)

print("🔄 Đang chạy lịch hằng ngày. Nhấn Ctrl+C để dừng.")

while True:
    schedule.run_pending()
    time.sleep(60)
