// ========== 检查登录状态 ==========
const userInfo = JSON.parse(localStorage.getItem('userInfo'));
if (!userInfo) {
  alert('未登录或会话已过期，请重新登录！');
  window.location.href = '/user/login';
}

const { role } = userInfo;

// ========== 根据角色定义跳转路径 ==========
const roleRoutes = {
  "STUDENT": [
    "/student/overview",
    "/user/search",
    "/user/settings",
    "/student/console"
  ],
  "COLLEGE_ADMIN": [
    "/college_admin/overview",
    "/user/search",
    "/user/settings",
    "/college_admin/console"
  ],
  "UNIVERSITY_ADMIN": [
    "/university_admin/overview",
    "/user/search",
    "/user/settings",
    "/university_admin/console"
  ]
};

// 默认 fallback 到学生路径
const urls = roleRoutes[role] || roleRoutes["STUDENT"];

// 配置粒子效果
particlesJS("particles-js", {
    "particles": {
        "number": {
            "value": 80, // 粒子数量
            "density": {
                "enable": true,
                "value_area": 800 // 粒子分布区域
            }
        },
        "color": {
            "value": "#ffffff" // 粒子颜色
        },
        "shape": {
            "type": "circle", // 粒子形状：circle, edge, triangle, polygon, star, image
            "stroke": {
                "width": 0,
                "color": "#000000"
            },
            "polygon": {
                "nb_sides": 5
            },
            "image": {
                "src": "img/github.svg",
                "width": 100,
                "height": 100
            }
        },
        "opacity": {
            "value": 0.5, // 粒子不透明度
            "random": false,
            "anim": {
                "enable": false,
                "speed": 1,
                "opacity_min": 0.1,
                "sync": false
            }
        },
        "size": {
            "value": 3, // 粒子大小
            "random": true, // 随机大小
            "anim": {
                "enable": false,
                "speed": 40,
                "size_min": 0.1,
                "sync": false
            }
        },
        "line_linked": {
            "enable": true, // 是否启用粒子之间的连线
            "distance": 150, // 连线的最大距离
            "color": "#ffffff",
            "opacity": 0.4,
            "width": 1
        },
        "move": {
            "enable": true, // 是否启用粒子移动
            "speed": 2, // 粒子移动速度
            "direction": "none", // 移动方向
            "random": false, // 是否随机移动
            "straight": false, // 是否直线移动
            "out_mode": "out", // 粒子移动出界后的模式：out, bounce
            "bounce": false,
            "attract": {
                "enable": false,
                "rotateX": 600,
                "rotateY": 1200
            }
        }
    },
    "interactivity": {
        "detect_on": "canvas", // 交互检测目标：canvas, window
        "events": {
            "onhover": {
                "enable": true, // 鼠标悬停时是否触发
                "mode": "repulse" // 悬停模式：grab, bubble, repulse
            },
            "onclick": {
                "enable": true, // 鼠标点击时是否触发
                "mode": "push" // 点击模式：push, remove, bubble, repulse
            },
            "resize": true // 是否响应窗口大小变化
        },
        "modes": {
            "grab": {
                "distance": 400,
                "line_linked": {
                    "opacity": 1
                }
            },
            "bubble": {
                "distance": 400,
                "size": 40,
                "duration": 2,
                "opacity": 8,
                "speed": 3
            },
            "repulse": {
                "distance": 200
            },
            "push": {
                "particles_nb": 4
            },
            "remove": {
                "particles_nb": 2
            }
        }
    },
    "retina_detect": true
  });
  
  // 设置画布宽高
  let width = window.innerWidth;
  let height = window.innerHeight - 60; // 减去导航栏高度
  
  // 创建 SVG 容器
  const svg = d3.select("#container")
  .append("svg")
  .attr("width", width)
  .attr("height", height);
  
  // 定义滤镜，添加发光效果
  const defsFilter = svg.append("defs");
  
  const glowFilter = defsFilter.append("filter")
  .attr("id", "glow");
  
  glowFilter.append("feGaussianBlur")
  .attr("stdDeviation", "4")
  .attr("result", "coloredBlur");
  
  const feMerge = glowFilter.append("feMerge");
  feMerge.append("feMergeNode")
  .attr("in", "coloredBlur");
  feMerge.append("feMergeNode")
  .attr("in", "SourceGraphic");
  
  // 设置圆盘的中心点和半径
  const centerX = width / 2; // 移除 +80
  const centerY = height / 2; // 移除 -35
  const outerRadius = Math.min(width, height) / 3; // 外半径
  const innerRadius = outerRadius * 0.7; // 内半径
  
  // 定义扇形数量
  const numSectors = 4; // 扇形数量
  const sectorAngle = 2 * Math.PI / numSectors;
  
  // 生成扇形数据
  const sectorsData = d3.range(numSectors).map((d, i) => ({
  startAngle: i * sectorAngle,
  endAngle: (i + 1) * sectorAngle,
  index: i,
  angle: (i + 0.5) * sectorAngle // 扇形中心角度
  }));
  
  // 创建圆盘组
  const diskGroup = svg.append("g")
  .attr("class", "disk")
  .attr("transform", `translate(${centerX}, ${centerY})`);
  
  // 弧生成器
  const arc = d3.arc()
  .innerRadius(innerRadius)
  .outerRadius(outerRadius);
  
  // 创建扇形组
  const sectorGroups = diskGroup.selectAll("g")
  .data(sectorsData)
  .enter()
  .append("g")
  .attr("class", "sector-group");
  
  // 绘制扇形路径
  sectorGroups.append("path")
  .attr("d", d => arc(d)) // 使用弧生成器生成路径
  .attr("fill", "transparent") // 填充透明，用于捕获鼠标事件
  .attr("stroke", "#ffffff") // 默认白色边框
  .attr("stroke-width", 2)
  .style("cursor", "pointer")
  .on("mouseover", function(event, d) {
    // 鼠标移入时，改变边框颜色和宽度
    d3.select(this)
      .transition()
      .duration(200)
      .attr("stroke", "#00ffff") // 边框变为亮青色
      .attr("stroke-width", 4); // 加粗边框
  
    // 扇形移动
    d3.select(this.parentNode)
      .transition()
      .duration(200)
      .attr("transform", function() {
        const offset = 10; // 移动距离
        const x = offset * Math.cos(d.angle - Math.PI / 2);
        const y = offset * Math.sin(d.angle - Math.PI / 2);
        return `translate(${x}, ${y})`;
      });
  })
  .on("mouseout", function() {
    // 鼠标移出时，恢复边框颜色和宽度
    d3.select(this)
      .transition()
      .duration(200)
      .attr("stroke", "#ffffff") // 恢复为白色边框
      .attr("stroke-width", 2); // 恢复边框宽度
  
    // 扇形回到原位
    d3.select(this.parentNode)
      .transition()
      .duration(200)
      .attr("transform", "translate(0,0)");
  })
  .on("click", function(event, d) {
    handleSectorClick(d.index);
  });
  
  // 添加扇形标签
  const labelTexts = [ "Overview",'search', "Settings", "Console"];  // 自定义标签文本
  
  // 初始化标签数组
  let labels = [];
  
    sectorGroups.append("text")
  .attr("transform", function(d, i) {
    const angle = (d.startAngle + d.endAngle) / 2;
    const x = Math.sin(angle) * (innerRadius + outerRadius) / 2;
    const y = -Math.cos(angle) * (innerRadius + outerRadius) / 2;
    
    // 获取对应的标签文本
    const labelText = labelTexts[i % labelTexts.length];
    
    // 存储每个标签的坐标和文本
    const labelData = {
      x: x,
      y: y,
      text: labelText
    };
    
    // 将标签数据存入 labels 数组
    labels.push(labelData);
    
    // 计算旋转角度
    let rotateAngle = (angle * 180 / Math.PI);
    
    // 如果是第一或第三个标签，增加180度
    if (i === 1 || i === 2||i===3) {
      rotateAngle += 180;
    }
    
    return `translate(${x}, ${y}) rotate(${rotateAngle})`;
  })
  .attr("text-anchor", "middle")
  .attr("alignment-baseline", "middle")
  .text(function(d, i) {
    return labelTexts[i % labelTexts.length];
  })
  .attr("class", "glow-text")
  .style("fill", "#ffffff")
  .style("pointer-events", "none")
  .style("filter", "url(#glow)");
  
  function handleSectorClick(index) {
  // 防止重复点击
  diskGroup.selectAll("path").on("click", null);

  // 动画上移并淡出
  diskGroup.transition()
    .duration(1000)
    .attr("transform", `translate(${centerX}, ${-outerRadius})`)
    .style("opacity", 0)
    .on("end", () => {
      // 直接使用顶部已定义的 urls（根据角色动态生成）
      if (index < urls.length) {
        window.location.href = urls[index];
      } else {
        console.warn("Invalid sector index:", index);
      }
    });
  }
  
  // 设置画布尺寸响应窗口变化
  window.addEventListener("resize", () => {
    width = window.innerWidth;
    height = window.innerHeight - 60; // 更新高度
    svg.attr("width", width).attr("height", height);
    // 更新中心点
    const newCenterX = width / 2; // 移除 +80
    const newCenterY = height / 2; // 移除 -35
    diskGroup.attr("transform", `translate(${newCenterX}, ${newCenterY})`);
  });