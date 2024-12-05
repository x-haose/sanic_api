# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.2.6] - 2023-07-05

### Fixed

- 修复配置类报错的问题

### Changed

- 升级sanic依赖版本为22.3
- 增加`setuptools`依赖

## [0.2.5] - 2023-04-09

### Added

- 支持捕获在中间件期间发生错误的异常情况
- 增加配置类功能
- 示例文件更新
- 工具方法中新增自动蓝图方法

### Changed

- 默认的json dumps方法改为orjson
- sanic 最低版本依赖更新至22.12
- 优化API响应封装及响应文档的生成

### Fixed

- 修复openapi tag重复的问题
- 修复日志级别判断不准问题

## [0.2.4] - 2023-02-05

### Fixed

- 修复示例文件不生效的问题

## [0.2.3] - 2023-02-03

### Fixed

- 修复无蓝图的api接口blueprint.ctx.desc报错的问题
- 实现_missing_方法，修复枚举基类无法识别枚举值的问题

### Changed

- 请求接口无参数时访问日志中不打印 “args:”
- 枚举基类字段类名称修改，避免重名

### Added

- API接口类支持自定义接口标签和接口描述
- 添加types-ujson包
- 自动生成的文档支持识别必须和可选参数
- 枚举基类增加to_desc方法列出枚举的所有描述

## [0.2.0] - 2023-01-19

### Changed

- api json序列化改为使用ujson
- 移除部分3.10以上的语法

### Added

- 日志功能优化改进:
    - 实现方式更加简洁优雅
    - 可按照类型去区分
    - 日志增加打印请求ID
- json响应体格式设置为可配置的
- 添加ujson包，移除orjson包
- 读取蓝图上面的 blueprint.ctx.desc 属性来代替name设置中文tag名
- 引入mypy、autoflake等代码检查工具
- 添加配置文件基类

## [0.1.1] - 2022-12-19

### Changed

- pip 首页的文件修改

## [0.1.0] - 2022-12-19

### Added

- 接口参数校验
- 接口文档生成
- 日志使用`loguru`代替
- 接口异常拦截
- 接口响应统一化
