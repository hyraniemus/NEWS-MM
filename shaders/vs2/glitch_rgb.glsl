/*
{
    "author": "Max Mittelbach",
    "color": "white",
    "movement": true,
    "parameters": [
        {
            "default": 0.5,
            "name": "chaos",
            "min": 0.0,
            "max": 1.0
        },
        {
            "default": 0.4,
            "name": "rgb_shift",
            "min": 0.0,
            "max": 0.08
        },
        {
            "default": 0.5,
            "name": "bands",
            "min": 4.0,
            "max": 40.0
        }
    ],
    "url": "",
    "uuid": "7c2e5a1f-8d3b-4e6a-9f0c-2b4d6e8a1c3f"
}
*/

#ifdef GL_ES
precision highp float;
#endif

float hash(float n) { return fract(sin(n) * 43758.5453); }
float hash2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

void main() {
    vec2 st = texCoord;

    // Per-band horizontal shift driven by chaos
    float bandY   = floor(st.y * bands);
    float bandT   = floor(time * 5.0);
    float isGlitch = step(1.0 - chaos * 0.6, hash(bandY + bandT * 73.0));
    float shift    = (hash(bandY + bandT * 137.0) * 2.0 - 1.0) * 0.06 * isGlitch;

    // RGB channels offset in opposite directions
    float r = hash2(vec2(st.x + shift + rgb_shift, st.y) + time * 0.007);
    float g = hash2(vec2(st.x + shift,             st.y) + time * 0.007 + 0.33);
    float b = hash2(vec2(st.x + shift - rgb_shift, st.y) + time * 0.007 + 0.66);

    // Horizontal scanline overlay
    float scan  = step(0.5, fract(st.y * 60.0 + time * 0.08));
    // Occasional full-row colour block
    float block = step(0.85, hash2(floor(st * vec2(18.0, 9.0)) + floor(time * 3.0)));

    vec3 col = color.rgb * vec3(r, g, b);
    col = mix(col * 0.1, col, block);
    col *= 0.6 + 0.4 * scan;
    col  = clamp(col, 0.0, 1.0);

    float coloredPixels = dot(col, vec3(1.0 / 3.0));
    fragColor = vec4(col, alpha * coloredPixels);
}
