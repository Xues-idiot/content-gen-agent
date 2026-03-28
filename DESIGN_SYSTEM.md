# Vox Design System

## 概述

Vox 前端使用一套精心设计的生产级设计系统，包含 **50+ 样式类** 和 **精选配色方案**，为用户提供高质量的视觉体验。

---

## 字体系统

### 主字体 (Display)
- **字体名称**: Sora
- **用途**: 标题、Logo、强调文字
- **字重**: 300, 400, 500, 600, 700, 800
- **特点**: 现代几何感，独特个性

### 正文字体 (Body)
- **字体名称**: Plus Jakarta Sans
- **用途**: 正文、按钮、标签
- **字重**: 300, 400, 500, 600, 700, 800
- **特点**: 优秀的可读性，优雅现代

### CSS 变量
```css
--font-display: 'Sora', -apple-system, BlinkMacSystemFont, sans-serif;
--font-body: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
```

---

## 配色系统

### 主色 (Primary - Violet/Indigo)
```
--color-primary: #5B21B6
--color-primary-50: #EDE9FE
--color-primary-100: #DDD6FE
--color-primary-200: #C4B5FD
--color-primary-300: #A78BFA
--color-primary-400: #8B5CF6
--color-primary-500: #7C3AED
--color-primary-600: #6D28D9
--color-primary-700: #5B21B6
--color-primary-800: #4C1D95
--color-primary-900: #3B0764
```

### 次色 (Secondary - Orange/Coral)
```
--color-secondary: #F97316
--color-secondary-50: #FFF7ED
--color-secondary-100: #FFEDD5
--color-secondary-200: #FED7AA
--color-secondary-300: #FDBA74
--color-secondary-400: #FB923C
--color-secondary-500: #F97316
--color-secondary-600: #EA580C
--color-secondary-700: #C2410C
--color-secondary-800: #9A3412
--color-secondary-900: #7C2D12
```

### 强调色 (Accent - Teal)
```
--color-accent: #0D9488
--color-accent-500: #14B8A6
--color-accent-600: #0D9488
```

### 强调色 2 (Rose)
```
--color-accent-rose: #F43F5E
--color-accent-rose-500: #F43F5E
```

### 中性色 (Warm Gray)
```
--color-neutral-50: #FAFAF9
--color-neutral-100: #F5F5F4
--color-neutral-200: #E7E5E4
--color-neutral-300: #D6D3D1
--color-neutral-400: #A8A29E
--color-neutral-500: #78716C
--color-neutral-600: #57534E
--color-neutral-700: #44403C
--color-neutral-800: #292524
--color-neutral-900: #1C1917
```

### 背景色
```
--color-bg-primary: #FEFCF9
--color-bg-secondary: #F8F6F3
--color-bg-tertiary: #F0EDE8
--color-bg-card: #FFFFFF
```

### 功能色
```
--color-success: #059669
--color-warning: #D97706
--color-error: #DC2626
--color-info: #2563EB
```

---

## 按钮系统 (50+ 变体)

### 主按钮
```css
.btn-primary - 渐变紫色按钮
.btn-secondary - 渐变橙色按钮
.btn-accent - 渐变青色按钮
```

### 轮廓按钮
```css
.btn-outline-primary - 紫色边框按钮
.btn-outline-secondary - 橙色边框按钮
.btn-outline-accent - 青色边框按钮
```

### 幽灵按钮
```css
.btn-ghost - 透明背景按钮
.btn-ghost-primary - 悬停时显示紫色
```

### 柔和按钮
```css
.btn-soft-primary - 柔和紫色背景
.btn-soft-secondary - 柔和橙色背景
.btn-soft-accent - 柔和青色背景
.btn-soft-rose - 柔和玫瑰色背景
```

### 按钮尺寸
```css
.btn-xs - 超小尺寸
.btn-sm - 小尺寸
.btn-md - 中等尺寸 (默认)
.btn-lg - 大尺寸
.btn-xl - 超大尺寸
```

### 按钮变体
```css
.btn-icon - 图标按钮
.btn-pill - 胶囊形状
.btn-square - 方形
```

### 使用示例
```jsx
<button className="btn btn-primary btn-lg">
  <Sparkles className="w-5 h-5" />
  开始生成
</button>
```

---

## 卡片系统

### 卡片类型
```css
.card - 默认卡片 (悬停阴影)
.card-bordered - 带边框卡片
.card-elevated - 提升阴影卡片
.card-glow-primary - 紫色发光效果
.card-glow-secondary - 橙色发光效果
.card-gradient-primary - 紫色渐变背景
.card-gradient-secondary - 橙色渐变背景
.card-gradient-accent - 青色渐变背景
```

### 卡片结构
```html
<div className="card">
  <div className="card-header">标题</div>
  <div className="card-body">内容</div>
  <div className="card-footer">底部</div>
</div>
```

---

## 输入系统

### 输入框
```css
.input - 默认输入框
.input-sm - 小尺寸输入框
.input-lg - 大尺寸输入框
.input-error - 错误状态
.input-success - 成功状态
```

### 文本域
```css
.textarea - 多行文本输入
```

### 选择框
```css
.select - 下拉选择框
```

### 使用示例
```jsx
<input
  type="text"
  className="input input-lg"
  placeholder="输入产品名称..."
/>
```

---

## 徽章/标签系统

### 徽章类型
```css
.badge-primary - 紫色徽章
.badge-secondary - 橙色徽章
.badge-accent - 青色徽章
.badge-rose - 玫瑰色徽章
.badge-success - 成功绿色徽章
.badge-warning - 警告黄色徽章
.badge-error - 错误红色徽章
.badge-neutral - 中性灰色徽章
```

### 标签
```css
.tag - 可移除标签
```

---

## 动画系统

### 淡入动画
```css
.fade-in - 基础淡入
.fade-in-up - 向上淡入
.fade-in-down - 向下淡入
.fade-in-left - 向左淡入
.fade-in-right - 向右淡入
```

### 缩放动画
```css
.scale-in - 基础缩放
.scale-in-up - 缩放淡入
```

### 滑动动画
```css
.slide-up - 向下滑入
.slide-down - 向上滑入
```

### 特效动画
```css
.shimmer - 闪烁加载效果
.pulse-glow - 脉冲发光效果
.float - 悬浮动画
.spin - 旋转动画
.bounce - 弹跳动画
```

---

## 视觉效果

### 玻璃效果
```css
.glass - 毛玻璃效果 (白色)
.glass-dark - 毛玻璃效果 (深色)
```

### 渐变背景
```css
.gradient-primary - 紫色渐变
.gradient-secondary - 橙色渐变
.gradient-accent - 青色渐变
.gradient-brand - 品牌渐变 (紫色到橙色)
.gradient-sunset - 日落渐变
.gradient-ocean - 海洋渐变
.gradient-warm - 暖色渐变
.mesh-gradient - 网格渐变
```

### 纹理效果
```css
.noise - 噪点纹理覆盖层
.dot-pattern - 点阵图案背景
.grid-pattern - 网格图案背景
```

---

## 阴影系统

### 基础阴影
```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07)
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08)
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.08)
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.15)
```

### 发光阴影
```css
--shadow-glow-primary: 0 0 20px rgba(91, 33, 182, 0.15)   // 紫色发光
--shadow-glow-secondary: 0 0 20px rgba(249, 115, 22, 0.15) // 橙色发光
--shadow-glow-accent: 0 0 20px rgba(13, 148, 136, 0.15)   // 青色发光
```

---

## 进度条系统

```css
.progress - 基础进度条容器
.progress-bar - 进度条
.progress-bar-primary - 紫色进度条
.progress-bar-secondary - 橙色进度条
.progress-bar-accent - 青色进度条
.progress-bar-success - 绿色进度条
.progress-bar-error - 红色进度条

// 尺寸
.progress-sm - 小进度条
.progress-lg - 大进度条
.progress-xl - 超大进度条
```

---

## 圆角系统

```css
--radius-xs: 0.125rem   /* 2px */
--radius-sm: 0.25rem    /* 4px */
--radius-md: 0.5rem     /* 8px */
--radius-lg: 0.75rem    /* 12px */
--radius-xl: 1rem       /* 16px */
--radius-2xl: 1.5rem    /* 24px */
--radius-3xl: 2rem      /* 32px */
--radius-full: 9999px   /* 圆形 */
```

---

## 头像系统

```css
.avatar - 基础头像
.avatar-xs - 超小 (1.5rem)
.avatar-sm - 小 (2rem)
.avatar-md - 中 (2.5rem)
.avatar-lg - 大 (3rem)
.avatar-xl - 超大 (4rem)
.avatar-2xl - 极大 (6rem)

// 颜色变体
.avatar-primary
.avatar-secondary
.avatar-accent
.avatar-rose
```

---

## 骨架屏加载

```css
.skeleton - 基础骨架屏
.skeleton-text - 文本骨架
.skeleton-title - 标题骨架
.skeleton-avatar - 头像骨架
.skeleton-button - 按钮骨架
```

---

## 平台品牌色

每个平台在 Vox 中都有专属配色：

| 平台 | 主色 | 渐变 |
|------|------|------|
| 小红书 | #EF4444 | from-red-500 to-rose-600 |
| 抖音 | #EC4899 | from-pink-500 to-fuchsia-600 |
| 公众号 | #3B82F6 | from-blue-500 to-indigo-600 |
| 朋友圈 | #10B981 | from-emerald-500 to-teal-600 |

---

## 设计原则

### 1. 字体选择
- 避免使用 Arial、Inter 等通用字体
- 选择独特、有个性的字体组合
- 标题使用 Sora，正文使用 Plus Jakarta Sans

### 2. 配色原则
- 主色使用深紫罗兰色 (#5B21B6)
- 次色使用温暖橙色 (#F97316) - 用户原有品牌色
- 强调色使用青绿色 (#0D9488) 提供对比
- 避免单调的紫色渐变白色背景

### 3. 动效原则
- 使用动画提升用户体验而非装饰
- 优先使用 CSS 动画，复杂动画使用 Motion 库
- 页面加载使用交错渐入效果
- 悬停状态添加微交互

### 4. 布局原则
- 意外的布局设计 (不对称、重叠、斜向流动)
- 大量负空间或受控密度
- 网格打破元素

### 5. 视觉效果
- 创造氛围和深度而非纯色背景
- 添加与整体美学匹配的纹理和效果
- 使用渐变网格、噪点纹理、几何图案

---

## 使用示例

### 完整页面结构
```jsx
<div className="min-h-screen bg-neutral-50">
  {/* 背景效果 */}
  <div className="fixed inset-0 -z-10">
    <div className="absolute inset-0 mesh-gradient" />
  </div>

  {/* 卡片 */}
  <div className="card card-elevated p-6">
    <div className="card-header">
      <h2 className="font-display text-lg font-bold">标题</h2>
    </div>
    <div className="card-body">
      {/* 内容 */}
    </div>
  </div>

  {/* 按钮 */}
  <button className="btn btn-primary btn-lg">
    <Sparkles className="w-5 h-5" />
    主操作
  </button>
</div>
```

---

## Deerflow 品牌

所有 Vox 前端界面必须包含 "Created By Deerflow" 签名：
- 位置: 页面右下角固定
- 样式: 半透明胶囊形状
- 交互: 悬停时显示紫色发光效果
- 链接: https://deerflow.tech (新标签页打开)

---

## 文件结构

```
frontend/src/
├── app/
│   ├── globals.css      # 全局样式和设计系统
│   ├── layout.tsx        # 根布局
│   └── page.tsx          # 首页
├── components/
│   ├── SidebarNav.tsx    # 侧边导航
│   ├── ProductInput.tsx  # 产品信息输入
│   ├── PlatformSelect.tsx # 平台选择
│   ├── CopyOutput.tsx    # 文案输出
│   └── ...
└── lib/
    └── api.ts           # API 工具函数
```

---

## 版本

- **版本**: 1.0.0
- **更新日期**: 2026-03-28
- **基于**: Deerflow Frontend Design Skill
