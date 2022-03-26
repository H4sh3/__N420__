

const arr = [{id: 'a'}, {id: 'b'}, {id: 'c'}];

const index = arr.findIndex(object => {
  return object.id === 'b';
});

console.log(index); 