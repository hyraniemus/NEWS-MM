/*
{
    "author": "Max Mittelbach",
    "color": "white",
    "movement": true,
    "parameters": [
        {
            "default": 0.5,
            "name": "scale",
            "min": 1.0,
            "max": 10.0
        },
        {
            "default": 0.6,
            "name": "layers",
            "min": 1.0,
            "max": 6.0
        },
        {
            "default": 0.5,
            "name": "saturation",
            "min": 0.0,
            "max": 2.0
        }
    ],
    "url": "",
    "uuid": "a9f2d7e4-1b5c-4a8e-b3f6-7d2e9a4c1f8b"
}
*/

#ifdef GL_ES
precision highp float;
#endif

const float TAU = 6.28318530718;

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec2 st = texCoord * scale;
    float t  = time;
    float v  = 0.0;

    v += sin(st.x + t);
    v += sin(st.y + t * 0.7);
    if (layers > 2.0) v += sin(st.x + st.y + t * 0.5);
    if (layers > 3.0) v += sin(length(st) * 2.0 + t);
    if (layers > 4.0) v += sin(st.x * 0.5 - st.y * 0.5 + t * 1.3);
    if (layers > 5.0) v += sin(length(st - vec2(scale * 0.5)) * 3.0 - t * 0.8);

    // Normalise to [0, 1]
    v = v / (layers * 2.0) + 0.5;

    float hue = fract(v * 0.7 + t * 0.04);
    vec3 plasma = hsv2rgb(vec3(hue, saturation, 1.0));

    vec3 col = clamp(plasma * color.rgb * 2.0, 0.0, 1.0);

    float coloredPixels = dot(col, vec3(1.0 / 3.0));
    fragColor = vec4(col, alpha * coloredPixels);
}
