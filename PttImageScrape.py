#   TODO: Download the image of ptt by input: pageNum, goodNum
import bs4, requests, re, random, os, threading, sys
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox

#   TODO: Get the index of url
def GetUrlIndex(url):
    soup  = GetHtml(url)
    nextBut = soup.find('a', string = '‹ 上頁')
    Index = nextBut.get('href')[-9:-5]
    return int(Index)+1

#   TODO: Pass over 18 of ptt and get html
def GetHtml(url):
    r = requests.Session()
    payload ={
        'from':'/bbs//index,html',
        'yes':'yes'
    }
    res = r.post('https://www.ptt.cc/ask/over18', data = payload)
    res = r.get(url)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    return soup

def PageDownlaod(index, i, goodNum, board):
    locals()['Page_' + str(i)] = Page(index, i, goodNum, board)
    locals()['Page_' + str(i)].GetArtitle()
    locals()['Page_' + str(i)].GetImageOfArtitcle(board)

class Page():
    def __init__(self, index, i, goodNum, board):
        self.url = 'http://www.ptt.cc/bbs/' + board + '/index' + str(index-i) + '.html'
        self.titleList = [] #Titles of this page with many good number 
        self.urlList = []   #Url of title above
        self.imageList = []
        self.goodNum = goodNum

    #   TODO: Get the title and the url of article
    def GetArtitle(self):
        soup = GetHtml(self.url)
        articleInfs = soup.find_all('div', class_ = 'r-ent')
        for articleInf in articleInfs:
            goodNumList = articleInf.select('.nrec span')    #Find the good number of every artile
            try:
                goodNumList[0].string
            except IndexError:  #No good number
                continue
            if goodNumList[0].string == u'\u7206':  #爆
                goodArticle = articleInf.select('.title a')
                self.titleList.append(goodArticle[0].string)
                self.urlList.append('http://www.ptt.cc' + goodArticle[0].get('href'))
            try: 
                int(goodNumList[0].string)
            except ValueError:  #like X5
                continue
            if int(goodNumList[0].string) > self.goodNum:
                goodArticle = articleInf.select('.title a')
                self.titleList.append(goodArticle[0].string)
                self.urlList.append('http://www.ptt.cc' + goodArticle[0].get('href'))


    #   TODO: Get the image of article
    def GetImageOfArtitcle(self, board):
        sameTitle = False
        for title, url in zip(self.titleList, self.urlList):  #For each article, to save the image
            #   TODO: Download image to file
            soup  = GetHtml(url)
            self.imageList  = soup.find_all('a', {'href' : re.compile(r'^https://i.imgur.com')})
            if self.imageList == []:    #No image in this article
                continue
            title = re.sub('[ ? , > , < , / , \\\\ , : , * ]', '', title)   #Illegal title name
            print(title + ': ' + url)
            imageNum = 1
            try:
                os.mkdir(board + '\\' + title)
            except FileExistsError as esc: #File already exists
                if not sameTitle:   #Same title but bot same page
                    sameTitle = True
                    imageNum = len(os.listdir(board + '\\' + title))
                    pass
                else:   #Same article is already downloaded
                    print('Problem: ', esc)
                    continue

            for imageUrl in self.imageList:
                print('Image{}: '.format(imageNum) + str(imageUrl.string))
                res = requests.get(imageUrl.string)
                try:
                    res.raise_for_status()
                except: #404
                    print('Not found for url: ' + imageUrl.string)
                imageFile = open(board + '\\' + title + '\\' + title + '_' + str(imageNum) + '.jpg', 'wb')
                for chunk in res.iter_content(100000):
                    imageFile.write(chunk)
                imageNum+=1
                imageFile.close()

class Gui():
    def __init__(self):
        #   Window set
        self.window = tk.Tk()
        self.window.title('Ptt Image Download')
        self.window.geometry('1024x768')
        self.window.configure(background = 'white')

        self.image=Image.open(r'C:\Users\King\Desktop\code\imgur.png')
        self.image=ImageTk.PhotoImage(self.image)
        self.imageLabel=tk.Label(self.window,image = self.image)
        self.imageLabel.pack()

        self.headerLabel = tk.Label(self.window, text = 'Ptt 圖片下載', background = 'white')
        self.headerLabel.pack()

        #   Url entry set
        self.urlFrame = tk.Frame(self.window)
        self.urlFrame.pack(side = tk.TOP, pady = 10)
        self.urlLabel  = tk.Label(self.urlFrame, text = '看板: ', background = 'white')
        self.urlLabel.pack(side = tk.LEFT)
        self.url = tk.StringVar()
        self.urlEntry = tk.Entry(self.urlFrame, textvariable = self.url)
        self.urlEntry.pack(side = tk.LEFT)

        #   Good number entry set
        self.goodFrame = tk.Frame(self.window)
        self.goodFrame.pack(side = tk.TOP, pady = 10)
        self.goodLabel  = tk.Label(self.goodFrame, text = '讚數: ', background = 'white')
        self.goodLabel.pack(side = tk.LEFT)
        self.goodNum = tk.StringVar()
        self.goodEntry = tk.Entry(self.goodFrame, textvariable = self.goodNum)
        self.goodEntry.pack(side = tk.LEFT)

        #   Page number entry set
        self.pageFrame = tk.Frame(self.window)
        self.pageFrame.pack(side = tk.TOP, pady = 10)
        self.pageLabel  = tk.Label(self.pageFrame, text = '頁數: ', background = 'white')
        self.pageLabel.pack(side = tk.LEFT)
        self.pageNum = tk.StringVar()
        self.pageEntry = tk.Entry(self.pageFrame, textvariable = self.pageNum)
        self.pageEntry.pack(side = tk.LEFT)

        #   Button set
        self.downloadBut = tk.Button(self.window, text = 'Downlaod', command = lambda: self.Start())
        self.downloadBut.pack()

        #   Download list set
        # self.downloadFrame = tk.Frame(self.window, background = 'white')
        # self.downloadFrame.pack(side = tk.BOTTOM)
        # self.downloadLabel = tk.Label(self.downloadFrame, text = 'Download List', background = 'white')
        # self.downloadLabel.pack()
        # self.listBox = tk.Listbox(self.downloadFrame, width = 60, height  = 23)
        # self.listBox.pack(side = tk.LEFT)
        # self.scrollBar  =tk.Scrollbar(self.downloadFrame)
        # self.scrollBar.pack(side = tk.LEFT, fill = 'y')
        # self.listBox.configure(yscrollcommand  = self.scrollBar.set)
        # self.scrollBar.configure(command = self.listBox.yview)

        self.window.mainloop()

#   TODO: Button function to create and start the thread
    def Start(self):
        pageNum = int(self.pageNum.get())    #The number of page to scrape
        goodNum = int(self.goodNum.get())    #The good number of article
        board = self.url.get()  #The board of ptt
        url = 'https://www.ptt.cc/bbs/' + board + '/index.html'    
        index = GetUrlIndex(url)    #The index of ptt web
        threads = []
        try:
            os.mkdir(board)
        except FileExistsError:
            None
        for i in range(pageNum):
            thread = threading.Thread(target = PageDownlaod, args = (index, i, goodNum, board,))
            threads.append(thread)
            thread.start()
        for i in range(len(threads)):
            threads[i].join()

        #   Message set
        self.message = tk.messagebox.showinfo(title = 'Download over!', message = 'Done!!!!!!')

if __name__ == '__main__':
    gui = Gui()