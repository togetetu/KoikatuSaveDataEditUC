#!/usr/bin/env python
import io
import msgpack
import json
import glob
import random
import os
import collections as cl
import codecs

UW_DIR = "./KKUC"


class KoikatuInners:

    def __init__(self):
        # データファイル格納先
        self.uw_dir = UW_DIR
        # 下着ファイル一覧
        self.inners = cl.OrderedDict()
        # 試着データ
        self.trys = cl.OrderedDict()

    # 下着ファイル新規登録
    def save_newinner(self,data):
        # データディレクトリ内のファイル数
        inners = glob.glob(UW_DIR +"/*.txt")
        # 保存
        f = open(UW_DIR +'/kkuc'+ '{:06}'.format(len(inners)) +'.txt','w')
        f.write(json.dumps(data))
        f.close()

    # 下着ファイル一覧が、未格納なら格納
    def set_inners(self,inners):
        if len(self.inners) == 0:
            self.inners = inners

    # 下着ファイル一覧をクリア
    def reset_inners(self):
        self.inners.clear()

    # 下着ファイル一覧を取得
    def get_inners(self):
        ret = cl.OrderedDict()
        inners = glob.glob(UW_DIR +"/*.txt")
        i = 0
        for inner in inners:
            ret[i] = os.path.basename(inner)
            i = i + 1
        return ret

    # 下着設定ファイルのパスを取得
    def get_equip_file_path(self,name):
        return UW_DIR +"/_equip_"+ name +".ini"

    # 下着設定ファイル読み込み＆更新
    def update_equip_file(self,name):
        # データ読み込み
        inners = self.inners                            # 下着ファイル一覧
        out_file_name = self.get_equip_file_path(name)  # 出力ファイル名
        # 下着設定ファイルの所在を確認
        if os.path.isfile(out_file_name) == False:
            self.create_equip_file(name)
        # 下着設定ファイル読み込み
        ret = self.read_equip_file(name)
        # 下着設定と今の下着ファイルを比較
        updateFlag = False
        for inner in inners.values():
            for i in range(0,7):
                if inner not in ret[str(i)].keys():
                    if i == 3 or i == 4:
                        ret[str(i)][inner] = 0
                    else:
                        ret[str(i)][inner] = 1
                    updateFlag = True
        # 下着が増えていたらファイルを更新
        if updateFlag == True:
            fh = codecs.open(out_file_name,"w+","utf-8")
            fh.write(json.dumps(ret,ensure_ascii=False,indent=4))
            fh.close
        return ret

    # 下着設定ファイルを読み込み
    def read_equip_file(self,name):
        out_file_name = self.get_equip_file_path(name)  # 出力ファイル名
        fh = codecs.open(out_file_name,"r","utf-8")
        ret = json.loads(fh.read())
        fh.close
        return ret

    # 下着設定ファイル新規作成
    def create_equip_file(self,name):
        # データ読み込み
        inners = self.inners                            # 下着ファイル一覧
        out_file_name = self.get_equip_file_path(name)  # 出力ファイル名
        # データ生成
        args = cl.OrderedDict()
        for i in range(0,7):
            args2 = cl.OrderedDict()
            for inner in inners.values():
                if i == 3:
                    args2[inner] = 0
                else:
                    args2[inner] = 1
            args[i] = args2
        # ファイル出力
        fh = codecs.open(out_file_name,"w","utf-8")
        fh.write(json.dumps(args,ensure_ascii=False,indent=4))
        fh.close

    # 下着設定データからホワイトリスト作成
    def get_equip_whitelist(self,dic,coordeNo):
        ret = []
        for name,flg in dic[str(coordeNo)].items():
            if flg == 1:
                if os.path.isfile(UW_DIR +"/"+ name):
                    ret.append(name)
        return ret

    # 試着セット
    def set_try(self,name,cloth):
        self.trys[name] = cloth

    # 下着チェンジャー
    def underware_random_change(self,equip,cloth,name,coordeNo):
        # unpack
        pack = msgpack.unpackb(cloth,encoding='utf-8')
        # 試着
        if coordeNo == 0 and name in self.trys:
            if self.trys[name] != "":
                # 下着ファイルからデータ取得
                f = open(UW_DIR +"/"+ self.trys[name],'r')
                dat = json.load(f)
                f.close()
                # データ格納
                pack["parts"][2] = dat["parts"][2]
                pack["parts"][3] = dat["parts"][3]
        # ランダムチェンジ
        else:
            # 下着のホワイトリスト取得
            wList = self.get_equip_whitelist(equip,coordeNo)
            if len(wList) > 0:
                # 抽選
                wCnt = len(wList)-1
                num = random.randint(0,wCnt)
                # 下着ファイルからデータ取得
                f = open(UW_DIR +"/"+ wList[num],'r')
                dat = json.load(f)
                f.close()
                # データ格納
                pack["parts"][2] = dat["parts"][2]
                pack["parts"][3] = dat["parts"][3]
        # pack
        cloth = msgpack.packb(pack, use_single_float=True, use_bin_type=True)
        return cloth