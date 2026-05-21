/*
{
    "author": "Max Mittelbach",
    "color": "white",
    "movement": true,
    "parameters": [
        {
            "default": 0.5,
            "name": "rings",
            "min": 3.0,
            "max": 30.0
        },
        {
            "default": 0.5,
            "name": "twist",
            "min": 0.0,
            "max": 10.0
        },
        {
            "default": 0.5,
            "name": "glow",
            "min": 0.5,
            "max": 8.0
        }
    ],
    "url": "",
    "uuid": "d4b8e2a6-9f1c-4d7b-a2e5-3c6f8d1b4e9a"
}
*/

#ifdef GL_ES
precision highp float;
#endif

const float PI  = 3.14159265359;
const float TAU = 6.28318530718;

void main() {
    // Centre and correct aspect ratio
    vec2 st = texCoord * 2.0 - 1.0;
    st.x *= resolution.x / resolution.y;

    float r = length(st);
    float a = atan(st.y, st.x);

    // Tunnel depth (closer to edge = farther in)
    float depth  = fract(1.0 / (r + 0.05) * 0.4 - time * 0.25);
    float angle  = fract(a / TAU + twist * depth * 0.08);

    // Glowing rings
    float ring  = abs(fract(depth * rings) - 0.5) * 2.0;
    ring  = pow(1.0 - ring, glow);

    // Spokes between rings
    float spoke = abs(fract(angle * 6.0) - 0.5) * 2.0;
    spoke = pow(1.0 - spoke, glow * 0.4);

    float pattern = max(ring, spoke * 0.6);

    // Colour cycles with depth and time
    float hue = fract(angle * 1.5 + depth * 0.3 + time * 0.06);
    vec4 K    = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 rgb  = abs(fract(hue + K.xyz) * 6.0 - K.www);
    vec3 neon = mix(K.xxx, clamp(rgb - K.xxx, 0.0, 1.0), 1.0);

    vec3 col = clamp(neon * color.rgb * pattern, 0.0, 1.0);

    float coloredPixels = dot(col, vec3(1.0 / 3.0));
    fragColor = vec4(col, alpha * coloredPixels);
}
