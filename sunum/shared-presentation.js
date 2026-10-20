window.TgPresentation={};(function(exports){"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.presentationSnapshot = presentationSnapshot;
/** Temporary presentation-only correction until the backend publishes the
 * verified Gyra kesiji asset. Never invent equipment or readings for real data.
 * Idempotent: an API supplied cutter always takes precedence. */
function presentationSnapshot(snapshot) {
    return __assign(__assign({}, snapshot), { lines: snapshot.lines.map(function (line) {
            if (line.id !== "gipsokarton" || line.mode !== "SIMULÝASIÝA" || line.equipment.some(function (e) { return e.assetKey === "gyra-kesiji"; }))
                return line;
            var dryer = line.equipment.find(function (e) { return e.assetKey === "guradyjy"; });
            var bundle = line.equipment.find(function (e) { return e.assetKey === "bukjalayjy"; });
            if (!dryer || !bundle)
                return line;
            var id = "presentation:gk:gyra-kesiji";
            var equipment = line.equipment.flatMap(function (e) { return e.id === bundle.id ? [
                { id: id, assetKey: "gyra-kesiji", name: "Gyra kesiji", kind: "process", order: e.order, status: e.status, mode: "SIMULÝASIÝA" },
                __assign(__assign({}, e), { order: e.order + 1 }),
            ] : [__assign(__assign({}, e), { order: e.kind !== "feed" && e.order > bundle.order ? e.order + 1 : e.order })]; });
            var flow = line.flow.flatMap(function (f) { return f.fromId === dryer.id && f.toId === bundle.id ? [
                __assign(__assign({}, f), { toId: id }),
                __assign(__assign({}, f), { fromId: id }),
            ] : [f]; });
            return __assign(__assign({}, line), { equipment: equipment, flow: flow });
        }) });
}
})(window.TgPresentation);