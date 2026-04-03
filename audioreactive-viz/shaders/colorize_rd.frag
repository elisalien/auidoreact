// ─── Reaction-Diffusion Colorizer ───
// Reads chemical state from simulation FBO and applies color palette

void main() {
    vec2 uv = v_uv;
    vec4 state = texture(u_feedback, uv);
    float a = state.r;
    float b = state.g;

    float edge = abs(a - b);
    float val = b;

    vec3 col = u_color1;
    col = mix(col, u_color2, smoothstep(0.05, 0.35, val));
    col = mix(col, u_color3, smoothstep(0.25, 0.55, val));
    col += u_color3 * edge * 2.0;
    col *= 0.7 + u_rms * 0.6;
    col += u_color2 * u_beat * 0.15;

    // Vignette
    float vig = 1.0 - 0.35 * length(uv - 0.5);
    col *= vig;

    fragColor = vec4(col, 1.0);
}
