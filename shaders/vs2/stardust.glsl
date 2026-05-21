/*
{
    "author": "Max Mittelbach",
    "color": "white",
    "movement": true,
    "parameters": [
        {
            "default": 0.4,
            "name": "density",
            "min": 20.0,
            "max": 300.0
        },
        {
            "default": 0.3,
            "name": "star_size",
            "min": 0.001,
            "max": 0.025
        },
        {
            "default": 0.5,
            "name": "twinkle",
            "min": 0.0,
            "max": 1.0
        }
    ],
    "url": "",
    "uuid": "f1c3e5b7-d9a2-4f8c-b6e4-2a5c7d9f1e3b"
}
*/

#ifdef GL_ES
precision highp float;
#endif

float hash(vec2 p) {
    p  = fract(p * vec2(443.897, 441.423));
    p += dot(p, p.yx + 19.19);
    return fract((p.x + p.y) * p.x);
}

void main() {
    vec2 st = texCoord;

    float stars = 0.0;

    // Three depth layers — each progressively finer and dimmer
    for (float i = 0.0; i < 3.0; i++) {
        float gridScale = density * 0.1 * (i + 1.0);
        vec2  grid      = st * gridScale;
        vec2  cell      = floor(grid);
        vec2  f         = fract(grid);

        // Random position within each cell
        vec2 pos = vec2(hash(cell + i * 17.3), hash(cell + i * 31.7 + 100.0));

        float dist       = length(f - pos);
        float sz         = star_size * (1.0 + i * 0.3);
        float brightness = 1.0 - smoothstep(0.0, sz, dist);

        // Optional twinkle per star
        float phase   = hash(cell + i) * 100.0 + time * (3.0 + i) * 4.0;
        float flicker = 0.5 + 0.5 * sin(phase);
        brightness   *= mix(1.0, flicker, twinkle);

        // Deeper layers are fainter
        stars += brightness / (i + 1.0);
    }

    stars = clamp(stars, 0.0, 1.0);
    vec3 col = color.rgb * stars;

    float coloredPixels = dot(col, vec3(1.0 / 3.0));
    fragColor = vec4(col, alpha * coloredPixels);
}
