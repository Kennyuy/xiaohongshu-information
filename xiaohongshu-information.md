# 小红书博主信息 - Xiaohongshu Blogger Information

> 项目创建时间：2026-03-16 21:32:32 (Asia/Shanghai)
> 数据来源：小红书 (Xiaohongshu/RedNote)

## 📊 测试数据 - 单依纯

### 博主信息

| 字段 | 值 |
|------|-----|
| 小红书 ID | 5de3f1030000000001001eda |
| 昵称 | 单依纯 |
| 粉丝数 | 3,158,989 |
| 获赞与收藏 | 12,123,729 |
| IP 属地 | 北京 |
| 简介 | 在这里分享我热爱的一切💕 |

### 笔记列表 (最新 5 篇)

| # | 标题 | 类型 | 点赞量 |
|---|------|------|--------|
| 1 | 《还有什么更好的》MV 上线 | 📹 视频 | 57,000 |
| 2 | 你就说神奇不神奇 | 📹 视频 | 100,000 |
| 3 | 二巡，来了 | 📝 图文 | 62,000 |
| 4 | 烟火向星辰，所愿皆成真 | 📝 图文 | 19,000 |
| 5 | 妈妈说拥有爱当然就很好，没有又能怎么呢？ | 📹 视频 | 56,000 |

## 🛠️ 项目文件

| 文件 | 说明 |
|------|------|
| [README.md](./README.md) | 项目文档和使用说明 |
| [xhs_crawler.py](./xhs_crawler.py) | 主爬虫脚本 |
| [requirements.txt](./requirements.txt) | Python 依赖 |
| [results.json](./results.json) | 完整爬取结果 (JSON 格式) |

## 🚀 使用方法

```bash
# 安装依赖
pip install -r requirements.txt

# 运行爬虫
python xhs_crawler.py --url <博主主页 URL> --cookie <Cookie> --output results.json
```

## ⚠️ 数据说明

由于小红书反爬机制，以下数据受限：
- 视频链接：无法获取（使用封面图作为预览）
- 完整图片列表：无法获取（仅第一张图片）
- 正文内容：无法获取（使用标题）
- 收藏量/评论量：无法获取（仅点赞量）

## 📄 License

MIT
