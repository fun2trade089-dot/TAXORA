import { Renderer, Camera, Geometry, Program, Mesh, Color } from 'ogl';
import { useEffect, useRef } from 'react';

const VERTEX = `#version 300 es
in vec2 position;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
}`;

const FRAGMENT = `#version 300 es
precision highp float;

uniform float uTime;
uniform float uAmplitude;
uniform float uBlend;
uniform vec3 uColorStops[3];
uniform vec2 uResolution;

out vec4 fragColor;

vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }

float snoise(vec2 v){
  const vec4 C = vec4(0.211324865405187, 0.366025403784439,
           -0.577350269189626, 0.024390243902439);
  vec2 i  = floor(v + dot(v, C.yy) );
  vec2 x0 = v -   i + dot(i, C.xx) ;
  vec2 i1;
  i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod(i, 289.0);
  vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
  + i.x + vec3(0.0, i1.x, 1.0 ));
  vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
    dot(x12.zw,x12.zw)), 0.0);
  m = m*m ;
  m = m*m ;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 a0 = x - floor(x + 0.5);
  vec3 norm = 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
  vec3  v1 = vec3(0.0);
  v1.x = a0.x  * x0.x  + h.x  * x0.y;
  v1.y = a0.y  * x12.x + h.y  * x12.y;
  v1.z = a0.z  * x12.z + h.z  * x12.w;
  return 130.0 * dot(m, v1);
}

void main() {
    vec2 uv = gl_FragCoord.xy / uResolution.xy;
    
    float noise1 = snoise(uv * 2.0 + uTime * 0.001 * 0.5);
    float noise2 = snoise(uv * 3.0 - uTime * 0.0015 * 0.5);
    
    float wave = sin(uv.x * 6.28318 + noise1 * uAmplitude) * 0.5 + 0.5;
    wave = smoothstep(0.2, 0.8, wave);
    
    vec3 col1 = mix(uColorStops[0], uColorStops[1], uv.x + noise1 * 0.2);
    vec3 col2 = mix(uColorStops[1], uColorStops[2], uv.y + noise2 * 0.2);
    vec3 finalCol = mix(col1, col2, wave * uBlend);
    
    fragColor = vec4(finalCol, 1.0);
}`;

interface AuroraProps {
    colorStops?: string[];
    amplitude?: number;
    blend?: number;
    speed?: number;
}

export default function Aurora({ 
    colorStops = ['#3A29FF', '#FF94B4', '#FF3232'], 
    amplitude = 1.0, 
    blend = 0.5, 
    speed = 1.0 
}: AuroraProps) {
    const activeRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const container = activeRef.current;
        if (!container) return;

        const renderer = new Renderer({
            alpha: true,
            premultipliedAlpha: false,
            antialias: true,
        });
        const gl = renderer.gl;
        container.appendChild(gl.canvas);

        const camera = new Camera(gl);
        camera.position.z = 1;

        const resize = () => {
            let width = container.clientWidth;
            let height = container.clientHeight;
            renderer.setSize(width, height);
            camera.perspective({ aspect: width / height });
        };
        window.addEventListener('resize', resize, false);
        resize();

        const geometry = new Geometry(gl, {
            position: { size: 2, data: new Float32Array([-1, -1, 3, -1, -1, 3]) },
        });

        const parsedColors = colorStops.map(c => new Color(c));

        const program = new Program(gl, {
            vertex: VERTEX,
            fragment: FRAGMENT,
            uniforms: {
                uTime: { value: 0 },
                uAmplitude: { value: amplitude },
                uBlend: { value: blend },
                uColorStops: { value: parsedColors },
                uResolution: { value: [gl.canvas.width, gl.canvas.height] },
            },
        });

        const mesh = new Mesh(gl, { geometry, program });

        let animationFrameId: number;
        const update = (t: number) => {
            animationFrameId = requestAnimationFrame(update);
            
            // Apply speed multiplier to time uniform
            program.uniforms.uTime.value = t * 0.01 * speed;
            
            program.uniforms.uResolution.value = [gl.canvas.width, gl.canvas.height];
            renderer.render({ scene: mesh, camera });
        };
        animationFrameId = requestAnimationFrame(update);

        return () => {
            cancelAnimationFrame(animationFrameId);
            window.removeEventListener('resize', resize);
            try {
                container.removeChild(gl.canvas);
            } catch (e) {}
            gl.getExtension('WEBGL_lose_context')?.loseContext();
        };
    }, [colorStops, amplitude, blend, speed]);

    return <div ref={activeRef} className="w-full h-full animate-fade-in" />;
}
