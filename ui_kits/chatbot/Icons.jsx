// Lucide-style stroke icons. 1.75 stroke, square caps, rounded joins, currentColor.
const Icon = ({ d, paths, size = 20, strokeWidth = 1.75, style }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={strokeWidth}
    strokeLinecap="round"
    strokeLinejoin="round"
    style={style}
    aria-hidden="true"
  >
    {paths ? paths.map((p, i) => <path key={i} d={p} />) : <path d={d} />}
  </svg>
);

const IconSend = (p) => (
  <Icon {...p} paths={["M22 2L11 13", "M22 2l-7 20-4-9-9-4 20-7z"]} />
);
const IconPlus = (p) => <Icon {...p} paths={["M12 5v14", "M5 12h14"]} />;
const IconClose = (p) => <Icon {...p} paths={["M18 6L6 18", "M6 6l12 12"]} />;
const IconChevronDown = (p) => <Icon {...p} d="M6 9l6 6 6-6" />;
const IconChevronUp = (p) => <Icon {...p} d="M18 15l-6-6-6 6" />;
const IconArrowDown = (p) => <Icon {...p} paths={["M12 5v14", "M19 12l-7 7-7-7"]} />;
const IconSparkle = (p) => (
  <Icon
    {...p}
    paths={[
      "M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z",
      "M19 14l.8 2.2L22 17l-2.2.8L19 20l-.8-2.2L16 17l2.2-.8z",
    ]}
  />
);
const IconBag = (p) => (
  <Icon
    {...p}
    paths={["M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z", "M3 6h18", "M16 10a4 4 0 0 1-8 0"]}
  />
);
const IconTruck = (p) => (
  <Icon
    {...p}
    paths={["M16 16h6v-5l-3-3h-3", "M2 16V5h14v11", "M9 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0z", "M21 18a2 2 0 1 1-4 0 2 2 0 0 1 4 0z"]}
  />
);
const IconShield = (p) => <Icon {...p} d="M12 2l8 4v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V6z" />;
const IconRotate = (p) => (
  <Icon {...p} paths={["M3 12a9 9 0 0 1 15-6.7L21 8", "M21 3v5h-5", "M21 12a9 9 0 0 1-15 6.7L3 16", "M3 21v-5h5"]} />
);
const IconDot = (p) => <Icon {...p} d="M12 12 m-3 0 a3 3 0 1 0 6 0 a3 3 0 1 0 -6 0" strokeWidth={0} />;
const IconAttach = (p) => (
  <Icon {...p} d="M21 11.5l-9.6 9.6a5 5 0 0 1-7-7l9.5-9.5a3.4 3.4 0 0 1 4.8 4.8L9.4 18.8a1.7 1.7 0 0 1-2.4-2.4l8.4-8.4" />
);
const IconMic = (p) => (
  <Icon
    {...p}
    paths={[
      "M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z",
      "M19 10v2a7 7 0 0 1-14 0v-2",
      "M12 19v4",
    ]}
  />
);

window.SSIcons = {
  IconSend, IconPlus, IconClose, IconChevronDown, IconChevronUp, IconArrowDown,
  IconSparkle, IconBag, IconTruck, IconShield, IconRotate, IconDot, IconAttach, IconMic,
};
