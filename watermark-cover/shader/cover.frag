#version 330 core

// ─────────────────────────────────────────────────────────────────────────────
//  Watermark Cover – combined overlay shader
//
//  TOP-LEFT  (x=25 y=25 w=70 h=70)  → esoteric gold sigil
//  BTM-RIGHT (x=1440 y=975 w=460 h=95) → anamorphic warm streak
//
//  Uniforms injected by render.py:
//    float time       – seconds since start
//    vec2  resolution – (1920, 1080)
// ─────────────────────────────────────────────────────────────────────────────

uniform float time;
uniform vec2  resolution;
out vec4 fragColor;

const float PI  = 3.14159265359;
const float TAU = 6.28318530718;

// ── Sigil geometry ────────────────────────────────────────────────────────────
// Video-space pixel coords (top-left origin)
const vec2  SIGIL_C = vec2(60.0, 60.0);   // centre of 70×70 box at (25,25)
const float SIGIL_R = 27.0;               // outer ring radius

// ── Anamorphic streak ─────────────────────────────────────────────────────────
const vec2  STREAK_C  = vec2(1670.0, 1022.5); // centre of 460×95 box at (1440,975)
const float STREAK_HW = 340.0;                // horizontal half-falloff
const float STREAK_HH = 20.0;                // vertical core half-height

// ── Helpers ───────────────────────────────────────────────────────────────────
vec2 rot2(vec2 p, float a) {
    float c = cos(a), s = sin(a);
    return vec2(c*p.x - s*p.y, s*p.x + c*p.y);
}

// ── Sigil: dashed outer ring (rotates) ───────────────────────────────────────
float dashedRing(vec2 p, float r, float nDash, float t) {
    float dist = abs(length(p) - r);
    float ring = smoothstep(2.5, 0.0, dist);
    float ang  = atan(p.y, p.x) + t * 0.22;
    float dash = step(0.38, fract(ang / TAU * nDash));
    return ring * dash;
}

// ── Sigil: equilateral triangle SDF (counter-rotates) ────────────────────────
float triSDF(vec2 p, float size) {
    float k = sqrt(3.0);
    p.x = abs(p.x) - size;
    p.y = p.y + size / k;
    if (p.x + k*p.y > 0.0) p = vec2(p.x - k*p.y, -k*p.x - p.y) * 0.5;
    p.x -= clamp(p.x, -2.0*size, 0.0);
    return -length(p) * sign(p.y);
}

float triangle(vec2 p, float size, float t) {
    p = rot2(p, -t * 0.13 + PI * 0.5);
    return smoothstep(1.8, 0.0, triSDF(p, size));
}

// ── Sigil: three spokes ───────────────────────────────────────────────────────
float spokes(vec2 p, float innerR, float outerR, float t) {
    float r   = length(p);
    float ang = atan(p.y, p.x) + t * 0.08;
    float seg = fract(ang / TAU * 3.0);
    float sp  = smoothstep(0.065, 0.0, min(seg, 1.0 - seg));
    float rm  = smoothstep(innerR - 2.0, innerR, r) * smoothstep(outerR + 2.0, outerR, r);
    return sp * rm;
}

// ── Sigil: outer triangle (slowly counter-rotates, large) ────────────────────
float outerTri(vec2 p, float t) {
    p = rot2(p, t * 0.07);
    return smoothstep(1.5, 0.0, abs(triSDF(p, SIGIL_R * 0.62)) - 1.0);
}

// ── Gold colour palette ───────────────────────────────────────────────────────
vec3 gold(float x) {
    // cosine palette: deep amber → bright gold → warm white
    vec3 a = vec3(0.72, 0.42, 0.06);
    vec3 b = vec3(0.18, 0.18, 0.10);
    vec3 c = vec3(1.00, 0.80, 0.55);
    vec3 d = vec3(0.00, 0.08, 0.18);
    return clamp(a + b * cos(TAU * (c * x + d)), 0.0, 1.0);
}

// ─────────────────────────────────────────────────────────────────────────────
void main() {
    // Convert OpenGL (bottom-left) → video-space (top-left)
    vec2 fc = vec2(gl_FragCoord.x, resolution.y - gl_FragCoord.y);

    float t      = time;
    float breath = 0.72 + 0.28 * sin(t * 1.35);

    vec4 col = vec4(0.0);

    // ── SIGIL ─────────────────────────────────────────────────────────────────
    {
        vec2 p = fc - SIGIL_C;
        float d = length(p);

        // Only compute inside padded region (saves fill-rate)
        if (d < SIGIL_R * 1.35) {
            float ring  = dashedRing(p, SIGIL_R, 16.0, t);
            float tri   = triangle(p, SIGIL_R * 0.40, t);
            float spk   = spokes(p, SIGIL_R * 0.16, SIGIL_R * 0.76, t);
            float otri  = outerTri(p, t) * 0.45;
            float ctr   = exp(-d * d / (SIGIL_R * 0.13 * SIGIL_R * 0.13));
            float halo  = exp(-d * d / (SIGIL_R * 0.70 * SIGIL_R * 0.70)) * 0.12;

            float intensity = max(max(ring, tri * 0.75),
                              max(max(spk * 0.65, ctr),
                              max(otri, halo))) * breath;

            vec3 gc = gold(d / SIGIL_R * 0.45 + t * 0.04);
            col = max(col, vec4(gc * intensity, intensity * 0.93));
        }
    }

    // ── ANAMORPHIC STREAK ─────────────────────────────────────────────────────
    {
        vec2 p = fc - STREAK_C;

        // Horizontal falloff: very gradual (anamorphic character)
        float xFall = exp(-p.x * p.x / (STREAK_HW * STREAK_HW * 2.2));

        // Vertical: tight core + wider soft wing (double-slit-ish)
        float yCore = exp(-p.y * p.y / (STREAK_HH * STREAK_HH * 0.38));
        float yWing = exp(-p.y * p.y / (STREAK_HH * STREAK_HH * 4.5)) * 0.22;

        // Subtle horizontal diffraction ripple
        float ripple = (0.5 + 0.5 * cos(p.x * 0.018)) * 0.14 * xFall;

        // Slow pulse + gentle shimmer along the streak
        float shimmer = 0.82 + 0.18 * sin(t * 0.85 + p.x * 0.007);

        float intensity = xFall * (yCore + yWing + ripple) * shimmer;

        // Colour: near-white core → warm amber → faint blue at far edges
        float tx = abs(p.x) / STREAK_HW;
        vec3 coreCol = vec3(1.00, 0.97, 0.88);
        vec3 midCol  = vec3(0.94, 0.62, 0.18);
        vec3 edgeCol = vec3(0.28, 0.42, 0.68);
        vec3 sc = mix(mix(coreCol, midCol, clamp(tx * 1.3, 0.0, 1.0)),
                      edgeCol, smoothstep(0.55, 1.0, tx));
        // Re-brighten at vertical centre
        sc = mix(sc, coreCol, yCore * 0.65);

        col = max(col, vec4(sc * intensity, intensity * 0.86));
    }

    fragColor = clamp(col, 0.0, 1.0);
}
