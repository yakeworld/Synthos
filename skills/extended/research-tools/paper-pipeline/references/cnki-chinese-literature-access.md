# CNKI/中文文献访问方法

> 中国知网（CNKI）是国内最大的学术文献数据库。Pdf-download-racing 覆盖外文期刊，本文件覆盖中文文献检索与下载。

## 开放通道（无需机构认证）

| 通道 | URL | 说明 | 限制 |
|:-----|:----|:-----|:-----|
| iData 知网镜像 | cnki.ixdao.cn | 知网镜像站，免费注册 | 每日限下载量（~5篇） |
| 全国图书馆参考咨询联盟 | ucdrs.superlib.net | 文献传递服务，免费 | 需注册，每次限1篇，人工处理 |
| CNKI Scholar | scholar.cnki.net | 知网学术搜索（开放检索） | 检索免费，全文需机构登录 |
| 百度学术 | xueshu.baidu.com | 多源聚合搜索 | 部分论文有OA版本可下载 |
| 上海图书馆远程访问 | library.sh.cn | 注册后可远程访问CNKI | 需上海图书馆读者证 |

## 机构认证通道

| 通道 | 说明 |
|:-----|:------|
| 温州人民医院图书馆 | 院内IP自动识别，可访问CNKI全文 |
| 温州医科大学图书馆 | 通过 fsso.cnki.net 机构认证登录 |
| 医院内网VPN | 通过医院VPN接入内网后直接访问 |

## Perl 工具集（用户自建）

位置：`/media/yakeworld/sda2/BaiduNetdiskWorkspace/Dropbox/perltool/`

### 脚本清单

| 脚本 | 大小 | 说明 |
|:-----|:----:|:------|
| getarticlev1.pl | 26KB | 单位科研论文自动化管理系统 v1，Tk GUI，CNKI+万方+维普三库合并 |
| getarticlev21.pl | 223KB | v21重写版，Tk+NoteBook GUI，支持按单位/作者/关键词检索 |
| btob.pl | 201KB | 桥接工具（bib to bib） |
| perltknew5.pl | 139KB | Tk工具 |
| perltknewzl3.pl | 89KB | Tk工具 v3 |

### CNKI 检索机制（getarticlev21.pl, 3856行）

#### 1. 旧版检索接口（epub.cnki.net）

```
http://epub.cnki.net/KNS/request/SearchHandler.ashx?action=&NaviCode=*&ua=1.21&
PageName=ASP.brief_result_aspx&DbPrefix=SCDB&
DbCatalog=中国学术文献网络出版总库&
ConfigFile=SCDB.xml&
db_opt=CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD&
expertvalue=AF % 单位名&
publishdate_from=2024-01-01&publishdate_to=2024-12-31&
his=0&__=时间戳
```

- `epub.cnki.net/kns/brief/brief.aspx` 翻页检索
- `FileNameS` 隐藏字段包含论文ID（格式：`数据库前缀!论文ID`）

**15页限制突破**：
- CNKI一次最多返回15页（750条）
- 脚本每检索14页后，清除cookies，重新调用 `SearchHandler.ashx` 获取新QueryID
- 新QueryID可继续翻页（写死 `$url` + `$mech->cookie_jar({})`）

#### 2. 引文导出接口（kns.cnki.net）

```
https://kns.cnki.net/KNS8/manage/ShowExport?filename={论文ID}&displaymode=NoteExpress&dbname={数据库名}
```

- 返回 NoteExpress 格式（含摘要、关键词、作者、机构等）
- 需要设置 `Referer: https://kns.cnki.net/`

#### 3. 目录预览接口（kreader.cnki.net）

```
http://kreader.cnki.net/Kreader/CatalogViewPage.aspx?dbCode=CJFQ&filename={论文ID}&tablename={数据库名}
```

- 返回论文目录/首页预览PDF

#### 4. 反爬对抗

```perl
$mech->agent('Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko');
$mech->add_header(Referer=>'https://kns.cnki.net/');
sleep rand(4);  # 随机等待
```

### AKNE知识库中的相关记录

在AKNE知识图谱的 `sources/work/投稿审核系统.md`（791行）中记录了完整的投稿审核系统开发文档，包含：

- **超星期刊下载**: `wget "http://qikan.chaoxing.com/search/openmag?isort=1&f=&searchdatatype=1&shouquankan=1&show=&size=9000"` 获取7398种期刊列表
- **中国期刊网爬取**: 使用 `WWW::Mechanize` + Perl爬取 qikanchina.net（期刊信息平台，非CNKI）
- **非法期刊识别**: 每期文章>80篇自动标记为可疑
- **Perl依赖**: `WWW::Mechanize`, `URI::Escape`, `Encode`, `HTTP::Cookies`, `Tk`

## 环境限制

当前服务器（DigitalOcean 加州，64.23.234.118）从境外访问CNKI：

| 接口 | 结果 | 说明 |
|:-----|:----:|:------|
| epub.cnki.net (HTTP) | HTTP 418 | 反爬拦截（接口活着，但被封锁） |
| kns.cnki.net (HTTPS) | SSL错误 | 连接被拒 |
| scholar.cnki.net | SSL错误 | 连接被拒 |
| kreader.cnki.net | SSL错误 | 连接被拒 |

**Perl脚本需要在医院内网/中国境内IP下运行**才能正常访问CNKI。

## 参考

- AKNE知识库: `sources/work/投稿审核系统.md`
- pdf-download-racing skill: 外文期刊PDF下载
- 用户Perl工具集: `/media/yakeworld/sda2/BaiduNetdiskWorkspace/Dropbox/perltool/`
