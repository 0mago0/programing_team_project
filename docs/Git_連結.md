# Git 連結與版本管理說明

## 1. 當前狀態

本工作區目前尚未建立遠端 Git 儲存庫，因此沒有可直接使用的 GitHub / GitLab 連結。若團隊需要提交報告，請先建立遠端倉庫並填入以下資訊。

## 2. GitHub / GitLab 模板

- GitHub Repo：https://github.com/<帳號>/<專題名稱>
- GitLab Repo：https://gitlab.com/<帳號>/<專題名稱>
- 版本分支：main

## 3. 建立方式（範例）

```bash
git init
git add .
git commit -m "Initialize campus planner project"
git branch -M main
git remote add origin https://github.com/<帳號>/<專題名稱>.git
git push -u origin main
```

## 4. 建議規範

- 主分支使用 main
- 功能分支命名例如：feature/role-A、feature/role-B
- 每次提交需附上簡短訊息，說明新增內容與測試狀態
- 需保留團隊共同版本紀錄，避免個人資料分散

## 5. 交付時使用方式

在報告中可寫成：

「本團隊專題之 Git 儲存庫已建置於 GitHub，連結如下：<請填寫實際連結>」

> 若尚未建立正式遠端連結，請先以此模板填入，待完成後再更新正式 URL。
