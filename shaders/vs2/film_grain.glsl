/*
{
    "author": "Max Mittelbach",
    "color": "#d8d8d8",
    "movement": true,
    "parameters": [
        {
            "default": 0.4,
            "name": "intensity",
            "min": 0.0,
            "max": 1.5
        },
        {
            "default": 0.35,
            "name": "scanlines",
            "min": 0.0,
            "max": 1.0
        },
        {
            "default": 0.45,
            "name": "vignette",
            "min": 0.0,
            "max": 3.0
        }
    ],
    "url": "",
    "uuid": "3f8a1b9c-2d4e-4f5a-8b7c-6e1d2a3f4b5c"
}
*/

#ifdef GL_ES
precision highp float;
#endif

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void main() {
    vec2 st  = texCoord;
    vec2 uv  = st * 2.0 - 1.0;

    // Film grain: different noise each frame via rapidly changing time offset
    float grain = hash(st + fract(time * 23.7));
    grain = (grain - 0.5) * intensity;

    // Scanlines: half-wave sine over pixel rows
    float scan = 0.5 + 0.5 * sin(st.y * resolution.y * 3.14159);
    scan = mix(1.0, pow(scan, 0.5), scanlines);

    // Radial vignette
    float vig = 1.0 - dot(uv, uv) * vignette * 0.25;
    vig = clamp(vig, 0.0, 1.0);

    vec3 col = clamp(color.rgb + vec3(grain), 0.0, 1.0);
    col *= scan * vig;

    float coloredPixels = dot(col, vec3(1.0 / 3.0));
    fragColor = vec4(col, alpha * coloredPixels);
}
